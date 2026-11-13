import hashlib
import json
import math
import os
import re
import socket
import threading
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path


class CopyError(Exception):
    pass


class Cancelled(CopyError):
    pass


class ApiError(CopyError):
    def __init__(self, status, code=None, retry_after=None, global_limit=False):
        self.status = status
        self.code = code
        self.retry_after = retry_after
        self.global_limit = global_limit
        hints = {401: "Token geçersiz veya süresi dolmuş.", 403: "Discord işlemi reddetti; yetkileri veya hesap doğrulamasını kontrol edin.",
                 404: "Sunucu, kanal veya üye bulunamadı."}
        if status == 429:
            wait_hint = (f" Discord {retry_after:.1f} saniye beklenmesini bildirdi." if retry_after is not None
                         else " Discord bir bekleme süresi bildirdi.")
            scope = " Global istek sınırı." if global_limit else ""
            message = "İşlem uzun süre otomatik bekletilmeden durduruldu; belirtilen süre dolmadan yeniden denemeyin."
            super().__init__(f"HTTP 429" + (f" / Discord {code}" if isinstance(code, int) else "") +
                             f": İstek sınırına ulaşıldı.{wait_hint}{scope} {message}")
            return
        super().__init__(f"HTTP {status}" + (f" / Discord {code}" if isinstance(code, int) else "") + ": " +
                         hints.get(status, "Discord işlemi tamamlamadı. Kısmi değişiklik olabilir; yeniden önizleyin."))


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class DiscordAPI:
    def __init__(self, token, cancel=None, log=lambda text: None, auth_mode="user"):
        if auth_mode not in ("user", "bot"):
            raise CopyError("Bilinmeyen kimlik doğrulama türü.")
        token = token.strip()
        if auth_mode == "bot":
            if token.lower().startswith("bot "):
                token = token[4:].strip()
            if not token or any(c.isspace() for c in token) or token.lower().startswith("bearer "):
                raise CopyError("Bot sürümünde geçerli bir bot token’i girin (Bot ön eki isteğe bağlıdır).")
            authorization = f"Bot {token}"
        else:
            if not token or any(c.isspace() for c in token) or token.lower().startswith(("bot ", "bearer ")):
                raise CopyError("Kullanıcı sürümünde kendi hesabınızın kullanıcı token’ini girin.")
            authorization = token
        if not token.isascii():
            raise CopyError("Token geçerli ASCII karakterlerinden oluşmalıdır.")
        self.auth_mode = auth_mode
        self._token = authorization
        self.cancel = cancel or threading.Event()
        self.log = log
        self.opener = urllib.request.build_opener(NoRedirect)
        self.next_mutation_request = 0

    def wait(self, seconds):
        if not math.isfinite(seconds) or not 0 <= seconds <= 600:
            raise CopyError("Discord bekleme süresi geçersiz veya 10 dakikadan uzun; işlem durdu.")
        if self.cancel.wait(seconds):
            raise Cancelled("Durduruldu. Tamamlanan değişiklikler geri alınmadı.")

    def request(self, method, path, data=None):
        if not path.startswith(("/guilds/", "/channels/", "/users/@me")) or ".." in path or "?" in path:
            raise CopyError("Geçersiz API yolu.")
        resource_mutation = method == "POST" or (method == "DELETE" and "/permissions/" not in path)
        for attempt in range(8):
            if resource_mutation and self.next_mutation_request:
                self.wait(max(0, self.next_mutation_request - time.monotonic()))
            body = None if data is None else json.dumps(data, ensure_ascii=False).encode("utf-8")
            req = urllib.request.Request("https://discord.com/api/v10" + path, data=body, method=method,
                                         headers={"Authorization": self._token, "Content-Type": "application/json",
                                                  "User-Agent": "ServerCopier/1.0 (local desktop utility)"})
            try:
                with self.opener.open(req, timeout=30) as response:
                    raw = response.read(8_000_001)
                    if len(raw) > 8_000_000:
                        raise CopyError("API yanıtı boyut sınırını aştı; işlem durdu.")
                    result = json.loads(raw) if raw else None
                    # Space resource creation/deletion operations 1.5 seconds apart.
                    # A route's X-RateLimit-Reset-After is NOT a global pause: a 200
                    # response with Remaining=0 must not freeze unrelated API routes.
                    if resource_mutation:
                        self.next_mutation_request = time.monotonic() + 1.5
                    return result
            except urllib.error.HTTPError as exc:
                try:
                    error = json.loads(exc.read(65536))
                except (ValueError, UnicodeError):
                    error = {}
                finally:
                    exc.close()
                if resource_mutation:
                    self.next_mutation_request = time.monotonic() + 1.5
                if not isinstance(error, dict):
                    error = {}
                if exc.code == 429:
                    try:
                        raw_delay = error.get("retry_after", exc.headers.get("Retry-After"))
                        delay = float(raw_delay) if raw_delay is not None else None
                        if delay is not None and not math.isfinite(delay):
                            delay = None
                    except (TypeError, ValueError):
                        delay = None
                    global_limit = bool(error.get("global")) or str(exc.headers.get("X-RateLimit-Global", "")).lower() == "true"
                    self.log("Discord 429 döndürdü; otomatik uzun bekleme yerine işlem durduruluyor.")
                    raise ApiError(429, error.get("code"), delay, global_limit) from None
                if method == "GET" and exc.code >= 500 and attempt < 2:
                    self.wait(2 ** attempt)
                    continue
                raise ApiError(exc.code, error.get("code")) from None
            except (urllib.error.URLError, TimeoutError, socket.timeout, ConnectionError, OSError):
                raise CopyError("Bağlantı kesildi veya zaman aşımı oluştu. Son isteğin sonucu belirsiz olabilir; tekrar önizleyin.") from None
            except (ValueError, UnicodeError):
                raise CopyError("Discord yanıtı okunamadı. Son isteğin sonucu belirsiz olabilir; tekrar önizleyin.") from None


def guild_id(value):
    value = value.strip()
    if not re.fullmatch(r"[0-9]{17,20}", value) or int(value) >= 2 ** 64:
        raise CopyError("Sunucu ID’si 17–20 rakam olmalıdır. Discord > Gelişmiş > Geliştirici Modu’nu açıp sunucu ID’sini kopyalayın.")
    return value


def snapshot(api, gid):
    return {"guild": api.request("GET", f"/guilds/{gid}"),
            "roles": api.request("GET", f"/guilds/{gid}/roles"),
            "channels": api.request("GET", f"/guilds/{gid}/channels")}


def fingerprint(state):
    guild = state["guild"]
    roles = [{"id": r["id"], "position": r.get("position", 0), "managed": bool(r.get("managed")),
              **role_payload(r)} for r in state["roles"]]
    channels = []
    for channel in state["channels"]:
        overwrites = [{"id": o["id"], "allow": str(int(o.get("allow") or 0)), "deny": str(int(o.get("deny") or 0))}
                      for o in channel.get("permission_overwrites", []) if o["type"] == 0]
        channels.append({"id": channel["id"], "name": channel["name"], "type": channel["type"],
                         "parent_id": channel.get("parent_id"), "position": channel.get("position", 0),
                         "permission_overwrites": sorted(overwrites, key=lambda o: o["id"])})
    relevant = {"guild": {k: guild.get(k) for k in ("id", "name", "owner_id")},
                "roles": sorted(roles, key=lambda r: r["id"]),
                "channels": sorted(channels, key=lambda c: c["id"])}
    return hashlib.sha256(json.dumps(relevant, sort_keys=True).encode()).hexdigest()


def role_payload(role):
    colors = role.get("colors") or {"primary_color": role.get("color", 0)}
    return {"name": role["name"], "colors": {"primary_color": colors.get("primary_color", 0)}}


def channel_payload(channel, roles, parents):
    kinds = {0: 0, 2: 2, 4: 4, 5: 0, 13: 2, 15: 15, 16: 0}
    if channel["type"] not in kinds:
        raise CopyError(f"Desteklenmeyen kanal türü: {channel['type']}. Hedefte hiçbir şey silinmedi.")
    result = {"name": channel["name"], "type": kinds[channel["type"]]}
    overwrites = []
    for entry in channel.get("permission_overwrites", []):
        if entry["type"] != 0:
            continue
        mapped = roles.get(entry["id"])
        if mapped is None:
            raise CopyError("Bir kanal izninin rolü kaynak rol listesinde yok. İşlem durduruldu.")
        overwrites.append({"id": mapped, "type": 0, "allow": str(entry.get("allow", "0")), "deny": str(entry.get("deny", "0"))})
    result["permission_overwrites"] = overwrites
    if channel.get("parent_id"):
        if channel["parent_id"] not in parents:
            raise CopyError("Bir kanalın üst kategorisi bulunamadı.")
        result["parent_id"] = parents[channel["parent_id"]]
    return result


def apply_channel_permissions(api, target_id, channel, created, payload, log):
    """Apply role overwrites only after every channel has been created and sorted."""
    requested = payload.get("permission_overwrites", [])
    everyone = next((item for item in requested if item["id"] == target_id), None)
    # Apply @everyone first so private channels become hidden before role grants.
    ordered = ([everyone] if everyone is not None else []) + [
        item for item in requested if item["id"] != target_id
    ]
    applied = []
    failures = 0
    for overwrite in ordered:
        try:
            api.request("PUT", f"/channels/{created['id']}/permissions/{overwrite['id']}",
                        {"type": 0, "allow": overwrite["allow"], "deny": overwrite["deny"]})
        except ApiError as permission_error:
            if permission_error.status in (400, 403) and permission_error.code == 50013:
                view_channel = 1 << 10
                if (overwrite["id"] == target_id
                        and int(overwrite.get("deny", "0")) & view_channel
                        and not int(overwrite.get("allow", "0")) & view_channel):
                    raise CopyError(
                        f"Kanal oluşturuldu ancak @everyone gizlilik izni uygulanamadı: "
                        f"{channel['name']}. Hedefte kanalı elle gizleyin. {permission_error}"
                    ) from None
                failures += 1
                log(f"İZİN AKTARILAMADI | Kanal: {channel['name']} · Rol ID: {overwrite['id']} · {permission_error}.")
                continue
            raise CopyError(f"Kanal izni uygulanamadı: {channel['name']} · Rol ID {overwrite['id']}. {permission_error}") from None
        except CopyError as permission_error:
            raise CopyError(
                f"Kanal izni uygulanırken bağlantı/işlem hatası: {channel['name']} · "
                f"Rol ID {overwrite['id']}. {permission_error}"
            ) from None
        applied.append(overwrite)

    if failures:
        log(f"GÜVENLİK UYARISI | {channel['name']}: Bazı rol izinleri uygulanamadı; hedef kanal izinlerini elle kontrol edin.")

    expected = dict(payload)
    expected["permission_overwrites"] = applied
    return expected, failures

def preview(api, source_id, target_id):
    source_id, target_id = guild_id(source_id), guild_id(target_id)
    if source_id == target_id:
        raise CopyError("Kaynak ve hedef aynı sunucu olamaz.")
    user = api.request("GET", "/users/@me")
    auth_mode = getattr(api, "auth_mode", "user")
    if auth_mode == "bot" and not user.get("bot"):
        raise CopyError("Bot sürümünde bir Discord bot token’i kullanmalısınız.")
    if auth_mode == "user" and user.get("bot"):
        raise CopyError("Kullanıcı sürümünde kullanıcı token’i kullanın; bot token’i için Bot sürümünü açın.")
    try:
        source = snapshot(api, source_id)
    except ApiError as exc:
        if auth_mode == "bot" and exc.status in (403, 404):
            raise CopyError("Bot kaynak sunucuya eklenmemiş veya sunucuyu okumak için gerekli erişime sahip değil. Botu kaynak sunucuya ekleyin ve kanal görüntüleme erişimi verin.") from None
        raise
    try:
        target = snapshot(api, target_id)
    except ApiError as exc:
        if auth_mode == "bot" and exc.status in (403, 404):
            raise CopyError("Bot hedef sunucuya eklenmemiş veya sunucuyu okumak için gerekli erişime sahip değil. Botu hedef sunucuya ekleyin.") from None
        raise
    is_owner = target["guild"].get("owner_id") == user["id"]
    member_role_ids = set()
    if not is_owner:
        try:
            member = api.request("GET", f"/guilds/{target_id}/members/{user['id']}")
        except ApiError as exc:
            if auth_mode == "bot" and exc.status in (403, 404):
                raise CopyError("Bot hedef sunucuda üye olarak bulunamadı. Botu hedef sunucuya ekleyip yeniden önizleyin.") from None
            raise
        member_role_ids = set(member.get("roles", []))
        assigned_role_ids = member_role_ids | {target_id}
        effective_permissions = 0
        for role in target["roles"]:
            if role["id"] in assigned_role_ids:
                effective_permissions |= int(role.get("permissions") or 0)
        if not effective_permissions & (1 << 3):
            if auth_mode == "bot":
                raise CopyError("Botun hedef sunucuda Yönetici (Administrator) yetkisi yok. Bot rolüne Administrator verin; bot rolü korunacaktır. Hiçbir şey silinmedi.")
            raise CopyError("Hedef sunucuda Yönetici (Administrator) yetkisi gerekiyor. Bu hedefte işlem yapılmadı.")
    protected_role_ids = sorted(member_role_ids)
    unmanageable_role_ids = []
    actor_top_role_position = None
    if not is_owner:
        actor_top_role_position = max(
            (int(r.get("position", 0)) for r in target["roles"] if r["id"] in member_role_ids),
            default=0
        )
        unmanageable_roles = [
            r for r in target["roles"]
            if r["id"] != target_id and not r.get("managed")
            and r["id"] not in member_role_ids
            and int(r.get("position", 0)) >= actor_top_role_position
        ]
        unmanageable_role_ids = sorted(r["id"] for r in unmanageable_roles)
    if auth_mode == "user" and unmanageable_role_ids:
        role_names = ", ".join(
            r["name"] for r in target["roles"] if r["id"] in set(unmanageable_role_ids)
        )
        raise CopyError(
            f"En üst rolün ({actor_top_role_position}. sıra), yönetilmesi gereken bazı hedef rollerin "
            f"üzerinde değil: {role_names}. Aktarımdan önce hesabın en üst rolünü bu rollerin üstüne "
            "taşıyın. Hiçbir şey silinmedi."
        )
    # A bot never reorders roles. It creates the source roles at Discord's default
    # safe position, and leaves every role outside its hierarchy completely alone.
    # The same fallback is used when the bot has too few hierarchy levels to
    # reproduce the source ordering exactly.
    skip_role_reorder = auth_mode == "bot"
    roles_to_create = len(source["roles"]) - 1
    if auth_mode == "user" and actor_top_role_position is not None and actor_top_role_position <= roles_to_create:
        raise CopyError(
            f"Kaynakta {roles_to_create} rol oluşturulacak; hesabın en üst rolü "
            f"{actor_top_role_position}. sırada. Yeni rollerin hiyerarşide altına yerleşebilmesi için "
            f"en üst rolünü en az {roles_to_create + 1}. sıraya taşıyın. Hiçbir şey silinmedi."
        )
    role_order_warning = bool(skip_role_reorder and
                              (unmanageable_role_ids or
                               (actor_top_role_position is not None and
                                actor_top_role_position <= roles_to_create)))
    if not source["roles"] or not any(r["id"] == source_id for r in source["roles"]):
        raise CopyError("Kaynak @everyone rolü okunamadı.")
    retained = [r for r in target["roles"] if r.get("managed")]
    if (len(source["roles"]) + len(retained) + len(protected_role_ids)
            + len(unmanageable_role_ids) > 250 or len(source["channels"]) > 500):
        raise CopyError("Hedefin Discord rol veya kanal sınırı aşılacak.")
    warnings = set()
    if retained:
        warnings.add(f"Hedefte Discord tarafından yönetilen {len(retained)} entegrasyon rolü korunacak; bunlar silinemez.")
    if protected_role_ids:
        subject = "Bot hesabına" if auth_mode == "bot" else "Hesabına"
        warnings.add(
            f"Hedefte {subject} atanmış {len(protected_role_ids)} rol silinmeyecek; "
            "kopyalama boyunca mevcut yetkilerin korunması için tutulacak."
        )
    if unmanageable_role_ids:
        protected_names = [r["name"] for r in target["roles"] if r["id"] in set(unmanageable_role_ids)]
        warnings.add(
            f"Rol hiyerarşisi nedeniyle {len(unmanageable_role_ids)} hedef rol değiştirilmeyecek "
            f"ve silinmeyecek: {', '.join(protected_names)}. Diğer aktarım adımları devam edecek."
        )
    if role_order_warning:
        warnings.add(
            "Bot rol hiyerarşisinin dışındaki rollere dokunmamak için yeni rollerin sıralaması "
            "Discord'un varsayılanında bırakılacak; mevcut hedef rollerin sırası değiştirilmeyecek."
        )
    if any(r.get("managed") for r in source["roles"]):
        warnings.add("Kaynak entegrasyon rolleri normal rol olarak oluşturulur; bot bağlantıları aktarılmaz.")
    if any(o["type"] != 0 for c in source["channels"] for o in c.get("permission_overwrites", [])):
        warnings.add("Kişiye özel kanal izinleri atlanır; yalnızca rollere verilen kanal izinleri aktarılır.")
    identity_roles = {r["id"]: r["id"] for r in source["roles"]}
    identity_parents = {c["id"]: c["id"] for c in source["channels"] if c["type"] == 4}
    unsupported_roots = {c["id"] for c in source["channels"] if c.get("type") == 20}
    skipped_ids = set(unsupported_roots)
    changed = True
    while changed:
        changed = False
        for channel in source["channels"]:
            if channel["id"] not in skipped_ids and channel.get("parent_id") in skipped_ids:
                skipped_ids.add(channel["id"])
                changed = True
    copy_channels, skipped_channels = [], []
    for channel in source["channels"]:
        if channel["id"] in skipped_ids:
            skipped_channels.append(channel)
            continue
        channel_payload(channel, identity_roles, identity_parents)
        copy_channels.append(channel)
    view_channel = 1 << 10
    private_channels = [
        c for c in copy_channels
        if any(o["type"] == 0 and o["id"] == source_id
               and int(o.get("deny", "0")) & view_channel
               and not int(o.get("allow", "0")) & view_channel
               for o in c.get("permission_overwrites", []))
    ]
    if private_channels:
        warnings.add(
            f"{len(private_channels)} gizli kanal/kategori önce izin tanımlanmadan oluşturulup sıralanacak; "
            "izinler son aşamada uygulanana kadar @everyone varsayılan görünürlüğü geçici olarak geçerli olabilir."
        )
    if unsupported_roots:
        dependent_count = len(skipped_channels) - len(unsupported_roots)
        warnings.add(
            f"Discord'un belgelenmiş kanal türleri arasında bulunmayan 20 türündeki "
            f"{len(unsupported_roots)} kanal ve bunlara bağlı {dependent_count} kanal atlanacak."
        )
    return {"source_id": source_id, "target_id": target_id, "source": source, "target": target,
            "copy_channels": copy_channels, "skipped_channels": skipped_channels,
            "user_id": user["id"], "auth_mode": auth_mode,
            "protected_role_ids": protected_role_ids,
            "unmanageable_role_ids": unmanageable_role_ids,
            "skip_role_reorder": skip_role_reorder,
            "warnings": sorted(warnings)}


def backup(plan, directory):
    directory = Path(directory)
    path = directory / (datetime.now().strftime("%Y%m%d-%H%M%S-%f") + "-" + plan["target_id"] + ".json")
    content = {"format": 1, "created_at": datetime.now().astimezone().isoformat(),
               "notice": "Yalnızca yapı kaydıdır. Mesajları/üyeleri içermez; otomatik geri yükleme değildir.",
               "source": plan["source"], "target_before": plan["target"]}
    try:
        directory.mkdir(parents=True, exist_ok=True)
        with path.open("x", encoding="utf-8") as file:
            json.dump(content, file, ensure_ascii=False, indent=2)
            file.flush()
            os.fsync(file.fileno())
    except OSError:
        raise CopyError("Yerel yapı yedeği yazılamadı; hedefte hiçbir şey silinmedi.") from None
    return path


def verify(api, plan, roles, channels, expected_channels, failed_deletions):
    final = snapshot(api, plan["target_id"])
    final_roles = {r["id"]: r for r in final["roles"]}
    final_channels = {c["id"]: c for c in final["channels"]}
    expected_role_ids = (set(roles.values())
                         | {r["id"] for r in plan["target"]["roles"] if r.get("managed")}
                         | set(plan.get("protected_role_ids", []))
                         | set(plan.get("unmanageable_role_ids", [])))
    if (not expected_role_ids <= set(final_roles) or set(final_roles) - expected_role_ids - set(failed_deletions["roles"])
            or not set(channels.values()) <= set(final_channels)
            or set(final_channels) - set(channels.values()) - set(failed_deletions["channels"])):
        raise CopyError("Son kontrolde rol/kanal listesi beklenenden farklı. İşlem kısmen tamamlanmış olabilir.")
    ordered = sorted(plan["source"]["roles"], key=lambda r: (r.get("position", 0), int(r["id"])))
    for role in ordered:
        if role["id"] == plan["source_id"]:
            continue
        actual = final_roles[roles[role["id"]]]
        expected = role_payload(role)
        if actual["name"] != expected["name"]:
            raise CopyError("Son kontrolde rol adı uyuşmadı.")
        colors = actual.get("colors") or {"primary_color": actual.get("color", 0)}
        if colors.get("primary_color") != expected["colors"]["primary_color"]:
            raise CopyError("Son kontrolde rol rengi uyuşmadı.")
    if not plan.get("skip_role_reorder", False):
        actual_order = sorted(ordered, key=lambda r: (final_roles[roles[r["id"]]]["position"], int(roles[r["id"]])))
        if [r["id"] for r in actual_order] != [r["id"] for r in ordered]:
            raise CopyError("Son kontrolde rol sırası uyuşmadı. Hedefi Discord’da inceleyin.")

    # These roles are explicitly outside the actor's hierarchy. Confirm their
    # existing properties survived unchanged; never PATCH, DELETE or reorder them.
    for role_id in plan.get("unmanageable_role_ids", []):
        original = next(r for r in plan["target"]["roles"] if r["id"] == role_id)
        actual = final_roles[role_id]
        for key in ("name", "permissions", "color", "hoist", "mentionable", "managed", "icon", "unicode_emoji"):
            if actual.get(key) != original.get(key):
                raise CopyError(
                    f"Korunan rolün bir özelliği dışarıdan değişti: {original['name']}. "
                    "Uygulama bu role yazma isteği göndermedi."
                )
    def permissions(value):
        return sorted((str(o["id"]), o["type"], str(o.get("allow", "0")), str(o.get("deny", "0"))) for o in value)
    for original_id, expected in expected_channels.items():
        actual = final_channels[channels[original_id]]
        if any(actual.get(k) != expected.get(k) for k in ("name", "type", "parent_id")) or permissions(actual.get("permission_overwrites", [])) != permissions(expected["permission_overwrites"]):
            raise CopyError("Son kontrolde kanal yapısı veya izinleri uyuşmadı. Hedefi Discord’da inceleyin.")
    groups = {}
    for channel in plan["source"]["channels"]:
        if channel["id"] not in channels:
            continue
        bucket = 2 if channel["type"] in (2, 13) else 4 if channel["type"] == 4 else 0
        groups.setdefault((channel.get("parent_id"), bucket), []).append(channel)
    for group in groups.values():
        # Discord normalizes numeric positions; relative order is the user-visible invariant.
        before = sorted(group, key=lambda c: (c.get("position", 0), int(c["id"])))
        after = sorted(group, key=lambda c: (final_channels[channels[c["id"]]].get("position", 0), int(channels[c["id"]])))
        if [c["id"] for c in before] != [c["id"] for c in after]:
            raise CopyError("Son kontrolde kanal sırası uyuşmadı. Hedefi Discord’da inceleyin.")
    return final


def execute(api, plan, directory, log=lambda text: None, progress=lambda done, total: None):
    fresh = preview(api, plan["source_id"], plan["target_id"])
    if fresh["user_id"] != plan["user_id"] or fresh.get("auth_mode", "user") != plan.get("auth_mode", "user"):
        raise CopyError("Kimlik doğrulama veya hesap önizlemeden sonra değişti. Yeniden önizleyin; hiçbir şey silinmedi.")
    if fresh.get("protected_role_ids", []) != plan.get("protected_role_ids", []):
        raise CopyError("Hedefte hesabına atanmış roller önizlemeden sonra değişti. Yeniden önizleyin; hiçbir şey silinmedi.")
    for side, label in (("source", "Kaynak"), ("target", "Hedef")):
        if fingerprint(fresh[side]) != fingerprint(plan[side]):
            raise CopyError(f"{label} sunucunun rol/kanal yapısı önizlemeden sonra değişti. Yeniden önizleyin; hiçbir şey silinmedi.")
    path = backup(fresh, directory)
    log(f"Yapı yedeği kaydedildi: {path}")
    source, target = fresh["source"], fresh["target"]
    copy_channels, skipped_channels = fresh["copy_channels"], fresh["skipped_channels"]
    sid, tid = fresh["source_id"], fresh["target_id"]
    protected_role_ids = set(fresh.get("protected_role_ids", []))
    unmanageable_role_ids = set(fresh.get("unmanageable_role_ids", []))
    deletable_roles = [r for r in target["roles"]
                       if r["id"] != tid and not r.get("managed")
                       and r["id"] not in protected_role_ids
                       and r["id"] not in unmanageable_role_ids]
    managed_roles = [r for r in target["roles"] if r.get("managed")]
    protected_roles = [r for r in target["roles"]
                       if r["id"] in protected_role_ids and not r.get("managed")]
    unmanageable_roles = [r for r in target["roles"] if r["id"] in unmanageable_role_ids]
    failed_deletions = {"roles": [], "channels": []}
    total = (len(target["channels"]) + len(deletable_roles) + len(managed_roles)
             + len(protected_roles) + len(unmanageable_roles)
             + len(source["roles"]) - 1 + len(source["channels"])
             + len(copy_channels) + 3)
    done = 0
    def step(text):
        nonlocal done
        done += 1
        log(text)
        progress(done, total)
    def delete(kind, item, route):
        try:
            api.request("DELETE", route)
        except Cancelled:
            raise
        except ApiError as exc:
            if exc.status == 429:
                raise
            failed_deletions[kind].append(item["id"])
            step(f"SİLİNEMEDİ | {'Rol' if kind == 'roles' else 'Kanal'}: {item['name']} ({item['id']}): {exc}")
        except CopyError as exc:
            failed_deletions[kind].append(item["id"])
            step(f"SİLİNEMEDİ | {'Rol' if kind == 'roles' else 'Kanal'}: {item['name']} ({item['id']}): {exc}")
        else:
            step(f"{'Rol' if kind == 'roles' else 'Kanal'} silindi: {item['name']}")

    for channel in skipped_channels:
        step(f"KOPYALANMADI | Kanal: {channel.get('name', 'isimsiz')} "
             f"({channel['id']}) · tür {channel['type']} veya atlanan üst kanal nedeniyle.")
    for channel in sorted(target["channels"], key=lambda c: c["type"] == 4):
        delete("channels", channel, f"/channels/{channel['id']}")
    for role in sorted(deletable_roles, key=lambda r: r.get("position", 0), reverse=True):
        delete("roles", role, f"/guilds/{tid}/roles/{role['id']}")
    for role in managed_roles:
        failed_deletions["roles"].append(role["id"])
        step(f"SİLİNEMEDİ | Rol: {role['name']} ({role['id']}): Discord tarafından yönetilen rol; devam ediliyor.")
    for role in protected_roles:
        step(f"KORUNDU | Rol: {role['name']} ({role['id']}) · Hesabına/Bot hesabına atanmış olduğu için silinmedi.")
    for role in unmanageable_roles:
        step(
            f"KORUNDU | Rol: {role['name']} ({role['id']}) · Botun rol hiyerarşisi nedeniyle "
            "değiştirilmeyecek veya silinmeyecek."
        )
    remaining = snapshot(api, tid)
    if len(remaining["roles"]) + len(source["roles"]) - 1 > 250 or len(remaining["channels"]) + len(copy_channels) > 500:
        raise CopyError("Silinemeyen öğeler nedeniyle Discord rol/kanal sınırı aşılacak. Kopyalama için hedefte yer açın.")
    role_map = {sid: tid}
    ordered_roles = sorted((r for r in source["roles"] if r["id"] != sid), key=lambda r: (r.get("position", 0), int(r["id"])))
    for role in ordered_roles:
        result = api.request("POST", f"/guilds/{tid}/roles", role_payload(role))
        role_map[role["id"]] = result["id"]
        step(f"Rol oluşturuldu: {role['name']}")
    if ordered_roles and not fresh.get("skip_role_reorder", False):
        api.request("PATCH", f"/guilds/{tid}/roles", [{"id": role_map[r["id"]], "position": i} for i, r in enumerate(ordered_roles, 1)])
        step("Rol sıralaması aktarıldı.")
    elif ordered_roles:
        step("Rol sıralaması atlandı: bot hiyerarşi sınırları içindeki rollere dokunulmadı.")
    else:
        step("Aktarılacak ek rol bulunmadı.")
    channel_map, expected_channels, created_channels, channel_payloads = {}, {}, {}, {}
    permission_failures = 0
    creation_order = sorted(copy_channels, key=lambda c: (c["type"] != 4, c.get("position", 0), int(c["id"])))
    for channel in creation_order:
        payload = channel_payload(channel, role_map, channel_map)
        creation_payload = dict(payload)
        creation_payload.pop("permission_overwrites", None)
        result = api.request("POST", f"/guilds/{tid}/channels", creation_payload)
        channel_map[channel["id"]] = result["id"]
        created_channels[channel["id"]] = result
        channel_payloads[channel["id"]] = payload
        step(f"Kanal oluşturuldu (ilk aşama izinsiz): {channel['name']}")
    if copy_channels:
        api.request("PATCH", f"/guilds/{tid}/channels", [
            {"id": channel_map[c["id"]], "position": c.get("position", 0)}
            for c in copy_channels
        ])
    step("Tüm kategori ve kanalların sıralaması aktarıldı.")

    # Only after creation and ordering are complete, apply source permission overwrites.
    for channel in creation_order:
        expected_payload, failed_permissions = apply_channel_permissions(
            api, tid, channel, created_channels[channel["id"]], channel_payloads[channel["id"]], log
        )
        expected_channels[channel["id"]] = expected_payload
        permission_failures += failed_permissions
        step(f"Kanal izinleri uygulandı: {channel['name']}")
    final = verify(api, fresh, role_map, channel_map, expected_channels, failed_deletions)
    step("Son kontrol geçti: kopyalanan roller, kanallar ve izinler doğrulandı.")
    return {"backup": path, "deletion_failures": sum(len(items) for items in failed_deletions.values()),
            "permission_failures": permission_failures,
            "remaining_roles": len({r["id"] for r in final["roles"]} & set(failed_deletions["roles"])),
            "remaining_channels": len({c["id"] for c in final["channels"]} & set(failed_deletions["channels"]))}
