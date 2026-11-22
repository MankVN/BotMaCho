import asyncio
import os
import random
import aiosqlite
import discord
from discord.ext import commands

DB_NAME = "bot_data.db"
BANNER_FILE = "13490.gif"
START_IMAGE_FILE = "images (27).jpeg"
NIGHT_IMAGE_FILE = "Bai-tho-anh-trang-700.jpg"
END_GIF_FILE = "minecraft-dog.gif"

WIN_COIN = 150
LOSE_COIN = 50

TIME_PRESETS = {
    "sieutoc": {
        "label": "Siêu tốc",
        "emoji": "⚡",
        "night": 30,
        "discuss": 15,
        "vote": 15,
        "summary": "⚡ Siêu tốc (🌙 Đêm: 30s | ☀️ Thảo luận: 15s | 🗳️ Bỏ phiếu: 15s)"
    },
    "binhthuong": {
        "label": "Bình thường",
        "emoji": "⚖️",
        "night": 120,
        "discuss": 60,
        "vote": 30,
        "summary": "⚖️ Bình thường (🌙 Đêm: 120s | ☀️ Thảo luận: 60s | 🗳️ Bỏ phiếu: 30s)"
    },
    "ruabo": {
        "label": "Rùa bò",
        "emoji": "🐢",
        "night": 180,
        "discuss": 120,
        "vote": 60,
        "summary": "🐢 Rùa bò (🌙 Đêm: 3m | ☀️ Thảo luận: 2m | 🗳️ Bỏ phiếu: 1m)"
    }
}

ALL_WEREWOLF_ROLES = {
    "danthuong": {
        "name": "Dân Làng",
        "team": "dan",
        "emoji": "👨‍🌾",
        "desc": "Không có kỹ năng ban đêm. Tham gia thảo luận và bỏ phiếu tìm Sói vào ban ngày."
    },
    "tientri": {
        "name": "Tiên Tri",
        "team": "dan",
        "emoji": "🔮",
        "desc": "Mỗi đêm được chọn soi 1 người để biết họ là người tốt hay kẻ xấu."
    },
    "baove": {
        "name": "Bảo Vệ",
        "team": "dan",
        "emoji": "🛡",
        "desc": "Mỗi đêm chọn bảo vệ 1 người khỏi bị Sói cắn (không bảo vệ 1 người 2 đêm liền)."
    },
    "phuthuy": {
        "name": "Phù Thủy",
        "team": "dan",
        "emoji": "🧪",
        "desc": "Có 1 bình cứu người bị sói cắn và 1 bình thuốc độc giết 1 người bất kỳ."
    },
    "thosan": {
        "name": "Thợ Săn",
        "team": "dan",
        "emoji": "🏹",
        "desc": "Khi bị giết hoặc bị treo cổ, được quyền bắn kéo theo 1 người chết cùng."
    },
    "cupid": {
        "name": "Thần Tình Yêu",
        "team": "dan",
        "emoji": "💘",
        "desc": "Đêm đầu tiên bắn mũi tên ghép đôi 2 người; một người chết, người kia chết theo."
    },
    "gialang": {
        "name": "Già Làng",
        "team": "dan",
        "emoji": "👴📜",
        "desc": "Chịu được 2 lần Sói cắn. Nếu bị dân làng treo cổ, cả làng sẽ mất hết kỹ năng."
    },
    "ducme": {
        "name": "Đức Mẹ Đồng Trinh",
        "team": "dan",
        "emoji": "💖",
        "desc": (
            "1) Khi có người bị treo cổ, Đức Mẹ có thể chọn chết thay. "
            "2) Có thể hy sinh bản thân để hồi sinh 1 người đã chết ở bất kỳ đêm nào trước đó "
            "(người được hồi sinh dùng được kỹ năng trong đêm đó; đến sáng cả hai đều chết)."
        ),
        "quotes": {
            "save_hanging": "Đức Mẹ với sự cao thượng của mình đã chọn chết thay cho con của Ngài",
            "revive_sacrifice": "Đức Mẹ đã tự hiến tế chính mình để Dân Làng có thể chiến thắng"
        }
    },
    "kedaomo": {
        "name": "Kẻ Đào Mộ",
        "team": "dan",
        "emoji": "🪏",
        "desc": (
            "Có thể đào mộ 1 người đã chết (không phân biệt đêm nào, không áp dụng cho phe Ma Chó) "
            "để sử dụng kỹ năng của role đó trong đêm đào. Mỗi người chỉ bị đào 1 lần, "
            "và đêm tiếp theo phải chọn người khác."
        ),
        "quotes": {
            "no_target": "Không có ai đủ điều kiện để bạn tác nghiệp"
        }
    },
    "phongdan": {
        "name": "Thằng Phổng Đạn",
        "team": "solo",
        "emoji": "💣",
        "min_players": 11,
        "desc": (
            "Solo (không có phe bạn, chỉ dành cho ván trên 10 người): Mỗi đêm có thể lôi kéo 1 người về phe. "
            "Khi số người theo phe bạn đông hơn số người còn sống còn lại, bạn thắng lập tức."
        ),
        "win_text": "Thằng Phổng Đạn {mention} Đã đảo chính. {mention} Chiến thắng !",
    },
    "masoi": {
        "name": "Sói",
        "team": "soi",
        "emoji": "🐺",
        "desc": "Thức dậy vào ban đêm để cùng đồng bọn chọn cắn 1 người chơi."
    },
    "soidau": {
        "name": "Sói Đầu Đàn",
        "team": "soi",
        "emoji": "🐺👑",
        "desc": "Thủ lĩnh bầy sói; có khả năng gây hiệu ứng đặc biệt hoặc quyết định mục tiêu."
    },
    "chanh": {
        "name": "Kẻ Chán Đời",
        "team": "solo",
        "emoji": "🤡",
        "desc": "Phe thứ 3: Thắng ngay lập tức nếu bị dân làng bỏ phiếu treo cổ vào ban ngày."
    }
}

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Duy nhất 1 phòng Ma Chó / 1 server tại 1 thời điểm
active_guild_games: dict[int, "WerewolfGame"] = {}


async def send_with_optional_image(
    channel: discord.abc.Messageable,
    embed: discord.Embed,
    image_path: str | None,
    content: str | None = None
):
    if image_path and os.path.exists(image_path):
        filename = os.path.basename(image_path)
        embed.set_image(url=f"attachment://{filename}")
        file = discord.File(image_path, filename=filename)
        try:
            return await channel.send(content=content, embed=embed, file=file)
        finally:
            try:
                file.close()
            except Exception:
                pass
    return await channel.send(content=content, embed=embed)


async def init_coin_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                balance INTEGER DEFAULT 0
            )
        """)
        await db.commit()


class TargetSelect(discord.ui.Select):
    def __init__(self, placeholder: str, options: list[discord.SelectOption], callback_fn):
        super().__init__(placeholder=placeholder[:150], min_values=1, max_values=1, options=options[:25])
        self.callback_fn = callback_fn

    async def callback(self, interaction: discord.Interaction):
        await self.callback_fn(interaction, self.values[0])


class SingleSelectView(discord.ui.View):
    def __init__(self, placeholder: str, options: list[discord.SelectOption], callback_fn, timeout: float = 30.0):
        super().__init__(timeout=timeout)
        self.add_item(TargetSelect(placeholder, options, callback_fn))


class DuckMotherSaveView(discord.ui.View):
    def __init__(self, target_member: discord.Member, timeout: float = 25.0):
        super().__init__(timeout=timeout)
        self.target_member = target_member
        self.save_choice: bool | None = None

    @discord.ui.button(label="Chết thay 💖", style=discord.ButtonStyle.danger)
    async def save_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.save_choice = True
        self.stop()
        await interaction.response.send_message(
            f"💖 Bạn đã chọn hy sinh thay cho **{self.target_member.display_name}**!",
            ephemeral=True
        )

    @discord.ui.button(label="Không chết thay", style=discord.ButtonStyle.secondary)
    async def skip_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.save_choice = False
        self.stop()
        await interaction.response.send_message("Bạn đã bỏ qua lượt cứu trên giá treo cổ.", ephemeral=True)


class VoteView(discord.ui.View):
    def __init__(self, alive_players: list[discord.Member], timeout: float = 30.0):
        super().__init__(timeout=timeout)
        self.votes: dict[int, int] = {}
        self.alive_ids = {p.id for p in alive_players}

        options = [discord.SelectOption(label="Bỏ phiếu trắng", value="skip", emoji="🏳️")]
        for p in alive_players[:24]:
            options.append(discord.SelectOption(label=p.display_name[:80], value=str(p.id), emoji="🗳️"))

        self.add_item(TargetSelect("Chọn người cần treo cổ ban ngày...", options, self.on_vote))

    async def on_vote(self, interaction: discord.Interaction, chosen_val: str):
        if interaction.user.id not in self.alive_ids:
            return await interaction.response.send_message("❌ Bạn đã bị loại hoặc không có trong ván.", ephemeral=True)

        if chosen_val == "skip":
            self.votes[interaction.user.id] = -1
            await interaction.response.send_message("🏳️ Bạn đã bỏ phiếu trắng.", ephemeral=True)
        else:
            target_id = int(chosen_val)
            self.votes[interaction.user.id] = target_id
            await interaction.response.send_message(f"🗳️ Bạn đã vote cho <@{target_id}>.", ephemeral=True)


class WerewolfGame:
    def __init__(self, host: discord.Member, lobby_channel: discord.TextChannel):
        self.host = host
        self.guild = lobby_channel.guild
        self.guild_id = lobby_channel.guild.id
        self.lobby_channel = lobby_channel
        self.game_channel: discord.TextChannel | None = None

        self.players: list[discord.Member] = [host]
        self.banned_roles: set[str] = set()
        self.assigned_roles: dict[int, str] = {}
        self.alive_ids: set[int] = set()
        self.dead_records: list[dict] = []
        self.gialang_lives: dict[int, int] = {}
        self.village_powers_disabled = False

        self.time_mode: str = "binhthuong"

        self.last_protected_id: int | None = None
        self.witch_heal_used = False
        self.witch_poison_used = False
        self.lovers: tuple[int, int] | None = None
        self.dug_grave_ids: set[int] = set()
        self.last_dug_id: int | None = None
        self.phongdan_cult_ids: set[int] = set()

        self.day_count = 0
        self.is_started = False
        self.is_finished = False
        self.message: discord.Message | None = None
        self.loop_task: asyncio.Task | None = None

    def get_timings(self) -> dict:
        return TIME_PRESETS[self.time_mode]

    def get_member(self, uid: int) -> discord.Member | None:
        return discord.utils.get(self.players, id=uid)

    def alive_members(self) -> list[discord.Member]:
        return [p for p in self.players if p.id in self.alive_ids]

    def build_embed(self) -> discord.Embed:
        player_list = "\n".join([f"• {p.mention}" for p in self.players]) if self.players else "Chưa có ai"
        available_names = [
            f"{info['emoji']} `{code}` ({info['name']}{' - 11+ người' if info.get('min_players') else ''})"
            for code, info in ALL_WEREWOLF_ROLES.items()
            if code not in self.banned_roles
        ]
        banned_names = [
            f"{ALL_WEREWOLF_ROLES[code]['emoji']} ~~{ALL_WEREWOLF_ROLES[code]['name']}~~ (`{code}`)"
            for code in self.banned_roles
        ]

        embed = discord.Embed(
            title="🐺 MA CHÓ - PHÒNG CHỜ",
            description=(
                f"**Chủ phòng:** {self.host.mention}\n"
                "**Quản trò:** Bot tự động điều phối Đêm / Ngày / Vote / Trả Coin\n\n"
                "Một lời nguyền đã giáng xuống ngôi làng yên bình. "
                "Hãy cùng nhau tìm ra những kẻ đội lốt cừu trước khi quá muộn!"
            ),
            color=discord.Color.from_rgb(47, 49, 54)
        )
        embed.add_field(name=f"👥 Người chơi ({len(self.players)}/16)", value=player_list, inline=False)
        embed.add_field(name="⏳ Nhịp độ thời gian", value=self.get_timings()["summary"], inline=False)
        embed.add_field(
            name="📜 List Role khả dụng",
            value=", ".join(available_names) if available_names else "Không có",
            inline=False
        )
        embed.add_field(
            name="🚫 Role bị Ban",
            value=", ".join(banned_names) if banned_names else "Không có role nào bị ban",
            inline=False
        )
        if os.path.exists(BANNER_FILE):
            embed.set_image(url=f"attachment://{BANNER_FILE}")
        embed.set_footer(text="Cần tối thiểu 3 người để bắt đầu • Tối đa 1 phòng / server")
        return embed

    async def create_private_room(self) -> discord.TextChannel:
        guild = self.guild
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            guild.me: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                manage_channels=True,
                manage_permissions=True
            )
        }
        for p in self.players:
            overwrites[p] = discord.PermissionOverwrite(
                view_channel=True,
                send_messages=False
            )

        category = self.lobby_channel.category
        room_name = f"🐺-ma-cho-{random.randint(100, 999)}"
        self.game_channel = await guild.create_text_channel(
            name=room_name,
            overwrites=overwrites,
            category=category,
            reason="Tạo phòng chơi Mini Game Ma Chó"
        )
        return self.game_channel

    async def set_room_chat_permission(self, can_chat: bool):
        if not self.game_channel:
            return
        for p in self.players:
            allow_send = can_chat and (p.id in self.alive_ids)
            await self.game_channel.set_permissions(
                p,
                view_channel=True,
                send_messages=allow_send
            )

    def mark_dead(self, uid: int) -> list[int]:
        if uid not in self.alive_ids:
            return []
        self.alive_ids.remove(uid)
        role_code = self.assigned_roles[uid]
        role_info = ALL_WEREWOLF_ROLES[role_code]
        member = self.get_member(uid)
        self.dead_records.append({
            "user_id": uid,
            "name": member.display_name if member else str(uid),
            "role": role_code,
            "team": role_info["team"],
            "night": self.day_count
        })
        newly_dead = [uid]

        if self.lovers and uid in self.lovers:
            partner_id = self.lovers[1] if self.lovers[0] == uid else self.lovers[0]
            if partner_id in self.alive_ids:
                newly_dead.extend(self.mark_dead(partner_id))

        return newly_dead

    async def award_coins(self, winner_ids: set[int], title: str, custom_message: str | None = None):
        if self.is_finished:
            return
        self.is_finished = True
        current_task = asyncio.current_task()
        if self.loop_task and not self.loop_task.done() and self.loop_task is not current_task:
            self.loop_task.cancel()

        winners_txt = []
        losers_txt = []

        async with aiosqlite.connect(DB_NAME) as db:
            for player in self.players:
                rcode = self.assigned_roles.get(player.id, "danthuong")
                rinfo = ALL_WEREWOLF_ROLES[rcode]
                await db.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (player.id,))
                if player.id in winner_ids:
                    reward = WIN_COIN
                    winners_txt.append(f"{rinfo['emoji']} {player.display_name} ({rinfo['name']})")
                else:
                    reward = LOSE_COIN
                    losers_txt.append(f"{rinfo['emoji']} {player.display_name} ({rinfo['name']})")
                await db.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (reward, player.id))
            await db.commit()

        active_guild_games.pop(self.guild_id, None)

        lobby_embed = discord.Embed(title=title, color=discord.Color.green())
        lobby_embed.add_field(name=f"🎉 Thắng (+{WIN_COIN} Coin)", value="\n".join(winners_txt) or "Không có", inline=False)
        lobby_embed.add_field(name=f"💀 Thua (+{LOSE_COIN} Coin)", value="\n".join(losers_txt) or "Không có", inline=False)

        await send_with_optional_image(self.lobby_channel, lobby_embed, END_GIF_FILE, content=custom_message)

        if self.game_channel:
            room_embed = discord.Embed(title=title, color=discord.Color.green())
            room_embed.add_field(name=f"🎉 Thắng (+{WIN_COIN} Coin)", value="\n".join(winners_txt) or "Không có", inline=False)
            room_embed.add_field(name=f"💀 Thua (+{LOSE_COIN} Coin)", value="\n".join(losers_txt) or "Không có", inline=False)
            await send_with_optional_image(self.game_channel, room_embed, END_GIF_FILE, content=custom_message)
            await self.game_channel.send("⏳ Phòng chơi riêng sẽ tự động xóa sau **15 giây**...")
            await asyncio.sleep(15)
            try:
                await self.game_channel.delete(reason="Kết thúc ván Ma Chó")
            except discord.Forbidden:
                pass

    async def check_game_end(self) -> bool:
        if self.is_finished:
            return True

        # Thằng Phổng Đạn thắng tức thì khi phe mình đông hơn số người sống còn lại
        for uid, rcode in self.assigned_roles.items():
            if rcode == "phongdan" and uid in self.alive_ids:
                cult_alive = len(self.alive_ids & self.phongdan_cult_ids)
                others_alive = len(self.alive_ids - self.phongdan_cult_ids)
                if cult_alive > others_alive:
                    pd_member = self.get_member(uid)
                    mention = pd_member.mention if pd_member else f"<@{uid}>"
                    win_msg = ALL_WEREWOLF_ROLES["phongdan"]["win_text"].format(mention=mention)
                    await self.award_coins(
                        winner_ids={uid},
                        title="💥 THẰNG PHỔNG ĐẠN ĐẢO CHÍNH THÀNH CÔNG!",
                        custom_message=f"💥 {win_msg}"
                    )
                    return True

        alive = self.alive_members()
        wolves_alive = [p for p in alive if ALL_WEREWOLF_ROLES[self.assigned_roles[p.id]]["team"] == "soi"]
        non_wolves_alive = [p for p in alive if ALL_WEREWOLF_ROLES[self.assigned_roles[p.id]]["team"] != "soi"]

        if len(wolves_alive) == 0:
            dan_winners = {
                p.id for p in self.players
                if ALL_WEREWOLF_ROLES[self.assigned_roles[p.id]]["team"] == "dan"
            }
            await self.award_coins(dan_winners, "🏆 DÂN LÀNG CHIẾN THẮNG!")
            return True

        if len(wolves_alive) >= len(non_wolves_alive):
            soi_winners = {
                p.id for p in self.players
                if ALL_WEREWOLF_ROLES[self.assigned_roles[p.id]]["team"] == "soi"
            }
            await self.award_coins(soi_winners, "🐺 PHE MA CHÓ CHIẾN THẮNG!")
            return True

        return False

    async def prompt_skill_for_role(self, actor: discord.Member, role_code: str, wolf_bite_target_id: int | None):
        if self.village_powers_disabled and ALL_WEREWOLF_ROLES[role_code]["team"] == "dan":
            return None

        alive = self.alive_members()
        result = {"bite_id": None, "protect_id": None, "poison_id": None, "heal": False}

        if role_code in ["masoi", "soidau"]:
            targets = [p for p in alive if ALL_WEREWOLF_ROLES[self.assigned_roles[p.id]]["team"] != "soi"]
            if not targets:
                return result
            opts = [discord.SelectOption(label=p.display_name[:80], value=str(p.id), emoji="🩸") for p in targets]
            chosen = {"val": None}

            async def cb(inter: discord.Interaction, val: str):
                chosen["val"] = int(val)
                await inter.response.send_message(f"🐺 Bạn đã chọn cắn <@{chosen['val']}> đêm nay.", ephemeral=True)

            try:
                view = SingleSelectView("Chọn người để Sói cắn đêm nay...", opts, cb, timeout=30.0)
                await actor.send("🌑 **Trời đã tối**, hãy chọn mục tiêu để cắn:", view=view)
                await view.wait()
                result["bite_id"] = chosen["val"]
            except discord.Forbidden:
                pass

        elif role_code == "baove":
            targets = [p for p in alive if p.id != self.last_protected_id]
            if not targets:
                return result
            opts = [discord.SelectOption(label=p.display_name[:80], value=str(p.id), emoji="🛡") for p in targets]
            chosen = {"val": None}

            async def cb(inter: discord.Interaction, val: str):
                chosen["val"] = int(val)
                await inter.response.send_message(f"🛡 Bạn đã bảo vệ <@{chosen['val']}> đêm nay.", ephemeral=True)

            try:
                view = SingleSelectView("Chọn người để bảo vệ đêm nay...", opts, cb, timeout=30.0)
                await actor.send("🛡 **Bảo Vệ**, hãy chọn 1 người để che chở khỏi Sói:", view=view)
                await view.wait()
                if chosen["val"]:
                    self.last_protected_id = chosen["val"]
                    result["protect_id"] = chosen["val"]
            except discord.Forbidden:
                pass

        elif role_code == "tientri":
            targets = [p for p in alive if p.id != actor.id]
            if not targets:
                return result
            opts = [discord.SelectOption(label=p.display_name[:80], value=str(p.id), emoji="🔮") for p in targets]
            chosen = {"val": None}

            async def cb(inter: discord.Interaction, val: str):
                chosen["val"] = int(val)
                r = ALL_WEREWOLF_ROLES[self.assigned_roles[chosen["val"]]]
                phe = "MA CHÓ" if r["team"] == "soi" else ("SOLO" if r["team"] == "solo" else "DÂN LÀNG")
                await inter.response.send_message(
                    f"🔮 Kết quả soi <@{chosen['val']}>: **{r['emoji']} {r['name']}** (Phe **{phe}**).",
                    ephemeral=True
                )

            try:
                view = SingleSelectView("Chọn người để Tiên Tri soi...", opts, cb, timeout=30.0)
                await actor.send("🔮 **Tiên Tri**, hãy chọn 1 người để soi vai trò:", view=view)
                await view.wait()
            except discord.Forbidden:
                pass

        elif role_code == "phuthuy":
            opts = []
            if not self.witch_heal_used and wolf_bite_target_id:
                victim = self.get_member(wolf_bite_target_id)
                if victim:
                    opts.append(discord.SelectOption(label=f"Cứu {victim.display_name[:65]}", value="heal", emoji="🧪"))
            if not self.witch_poison_used:
                for p in alive[:22]:
                    if p.id != actor.id:
                        opts.append(discord.SelectOption(label=f"Độc {p.display_name[:65]}", value=f"poison:{p.id}", emoji="☠️"))
            opts.append(discord.SelectOption(label="Không dùng bình nào", value="none", emoji="⏭️"))

            async def cb(inter: discord.Interaction, val: str):
                if val == "heal" and not self.witch_heal_used:
                    self.witch_heal_used = True
                    result["heal"] = True
                    await inter.response.send_message("🧪 Bạn đã dùng bình cứu!", ephemeral=True)
                elif val.startswith("poison:") and not self.witch_poison_used:
                    self.witch_poison_used = True
                    pid = int(val.split(":")[1])
                    result["poison_id"] = pid
                    await inter.response.send_message(f"☠️ Bạn đã dùng bình độc lên <@{pid}>!", ephemeral=True)
                else:
                    await inter.response.send_message("⏭️ Bạn đã bỏ qua lượt đêm nay.", ephemeral=True)

            try:
                view = SingleSelectView("Phù Thủy chọn hành động...", opts, cb, timeout=30.0)
                victim_txt = f"<@{wolf_bite_target_id}> đang bị Sói cắn." if wolf_bite_target_id else "Đêm nay không ai bị Sói cắn."
                await actor.send(f"🧪 **Phù Thủy**, {victim_txt}", view=view)
                await view.wait()
            except discord.Forbidden:
                pass

        elif role_code == "cupid" and self.day_count == 1 and not self.lovers:
            if len(alive) >= 2:
                pair = random.sample([p.id for p in alive], 2)
                self.lovers = (pair[0], pair[1])
                try:
                    await actor.send(f"💘 **Thần Tình Yêu** đã ghép đôi <@{pair[0]}> và <@{pair[1]}>!")
                except discord.Forbidden:
                    pass

        elif role_code == "phongdan":
            targets = [p for p in alive if p.id != actor.id and p.id not in self.phongdan_cult_ids]
            if targets:
                opts = [discord.SelectOption(label=p.display_name[:80], value=str(p.id), emoji="💥") for p in targets]
                chosen = {"val": None}

                async def cb(inter: discord.Interaction, val: str):
                    chosen["val"] = int(val)
                    await inter.response.send_message(f"💥 Bạn đã lôi kéo <@{chosen['val']}> về phe mình!", ephemeral=True)

                try:
                    view = SingleSelectView("Chọn người để lôi kéo về phe Phổng Đạn...", opts, cb, timeout=30.0)
                    await actor.send("💥 **Thằng Phổng Đạn**, chọn 1 người để lôi kéo đêm nay:", view=view)
                    await view.wait()
                    if chosen["val"]:
                        self.phongdan_cult_ids.add(chosen["val"])
                except discord.Forbidden:
                    pass

        elif role_code == "kedaomo":
            eligible = [
                rec for rec in self.dead_records
                if rec["team"] != "soi"
                and rec["user_id"] not in self.dug_grave_ids
                and rec["user_id"] != self.last_dug_id
            ]
            if not eligible:
                try:
                    await actor.send(f"🪏 {ALL_WEREWOLF_ROLES['kedaomo']['quotes']['no_target']}")
                except discord.Forbidden:
                    pass
                return result

            opts = [
                discord.SelectOption(
                    label=f"{rec['name'][:50]} ({ALL_WEREWOLF_ROLES[rec['role']]['name']})",
                    value=str(rec["user_id"]),
                    emoji="🪏"
                )
                for rec in eligible
            ]
            chosen = {"rec": None}

            async def cb(inter: discord.Interaction, val: str):
                uid = int(val)
                chosen["rec"] = next((r for r in eligible if r["user_id"] == uid), None)
                if chosen["rec"]:
                    await inter.response.send_message(
                        f"🪏 Bạn đã đào mộ **{chosen['rec']['name']}** và mượn kỹ năng **{ALL_WEREWOLF_ROLES[chosen['rec']['role']]['name']}**!",
                        ephemeral=True
                    )

            try:
                view = SingleSelectView("Chọn mộ để đào và dùng kỹ năng đêm nay...", opts, cb, timeout=30.0)
                await actor.send("🪏 **Kẻ Đào Mộ**, hãy chọn 1 người đã chết để đào mộ:", view=view)
                await view.wait()
                if chosen["rec"]:
                    target_rec = chosen["rec"]
                    self.dug_grave_ids.add(target_rec["user_id"])
                    self.last_dug_id = target_rec["user_id"]
                    borrowed_role = target_rec["role"]
                    if borrowed_role not in ["kedaomo", "danthuong"]:
                        sub_res = await self.prompt_skill_for_role(actor, borrowed_role, wolf_bite_target_id)
                        if sub_res:
                            result.update(sub_res)
            except discord.Forbidden:
                pass

        return result

    async def handle_ducme_night_revive(self) -> list[int]:
        if self.village_powers_disabled or not self.dead_records or not self.game_channel:
            return []

        ducme_member = None
        for uid, rcode in self.assigned_roles.items():
            if rcode == "ducme" and uid in self.alive_ids:
                ducme_member = self.get_member(uid)
                break

        if not ducme_member:
            return []

        opts = [discord.SelectOption(label="Không hy sinh đêm nay", value="skip", emoji="⏭️")]
        for rec in self.dead_records[:24]:
            rinfo = ALL_WEREWOLF_ROLES[rec["role"]]
            opts.append(
                discord.SelectOption(
                    label=f"Hồi sinh {rec['name'][:45]} ({rinfo['name']})",
                    value=str(rec["user_id"]),
                    emoji="💖"
                )
            )

        chosen_dead_id = {"val": None}

        async def cb(inter: discord.Interaction, val: str):
            if val != "skip":
                chosen_dead_id["val"] = int(val)
                await inter.response.send_message(
                    f"💖 Bạn đã chọn tự hiến tế để hồi sinh <@{chosen_dead_id['val']}> trong đêm nay!",
                    ephemeral=True
                )
            else:
                await inter.response.send_message("Bạn giữ nguyên mạng sống đêm nay.", ephemeral=True)

        try:
            view = SingleSelectView("Đức Mẹ: Chọn người đã chết để hồi sinh...", opts, cb, timeout=30.0)
            await ducme_member.send("💖 **Đức Mẹ Đồng Trinh**, bạn có muốn hy sinh bản thân để hồi sinh 1 người đã chết?", view=view)
            await view.wait()
        except discord.Forbidden:
            return []

        revived_uid = chosen_dead_id["val"]
        if not revived_uid:
            return []

        revived_member = self.get_member(revived_uid)
        revived_role = self.assigned_roles[revived_uid]

        self.alive_ids.add(revived_uid)
        await self.game_channel.send(f"💖 {ALL_WEREWOLF_ROLES['ducme']['quotes']['revive_sacrifice']}")

        if revived_member and revived_role not in ["danthuong", "ducme"]:
            await self.prompt_skill_for_role(revived_member, revived_role, wolf_bite_target_id=None)

        sacrificed_pair = []
        sacrificed_pair.extend(self.mark_dead(ducme_member.id))
        sacrificed_pair.extend(self.mark_dead(revived_uid))
        return sacrificed_pair

    async def handle_ducme_hanging_save(self, accused: discord.Member) -> discord.Member | None:
        if self.village_powers_disabled or not self.game_channel:
            return None

        for uid, rcode in self.assigned_roles.items():
            if rcode == "ducme" and uid in self.alive_ids and uid != accused.id:
                ducme_member = self.get_member(uid)
                if not ducme_member:
                    continue
                view = DuckMotherSaveView(accused, timeout=25.0)
                try:
                    await ducme_member.send(
                        f"💖 **{accused.display_name}** sắp bị treo cổ! Bạn có muốn chết thay không?",
                        view=view
                    )
                    await view.wait()
                    if view.save_choice is True:
                        await self.game_channel.send(f"💖 {ALL_WEREWOLF_ROLES['ducme']['quotes']['save_hanging']}")
                        return ducme_member
                except discord.Forbidden:
                    pass
        return None

    async def run_game_loop(self):
        try:
            while not self.is_finished and self.game_channel:
                self.day_count += 1
                timings = self.get_timings()

                # 1. BAN ĐÊM - KHÓA CHAT + ẢNH MỖI ĐÊM
                await self.set_room_chat_permission(can_chat=False)
                night_embed = discord.Embed(
                    title=f"🌙 ĐÊM THỨ {self.day_count} ({timings['night']}s)",
                    description=(
                        "Kênh chat đã khóa! Các vai trò đặc biệt vui lòng kiểm tra tin nhắn riêng (DM) từ bot..."
                    ),
                    color=discord.Color.dark_blue()
                )
                await send_with_optional_image(self.game_channel, night_embed, NIGHT_IMAGE_FILE)

                wolf_votes = []
                protected_id = None
                witch_heal = False
                witch_poison_id = None
                witch_members: list[discord.Member] = []

                for player in list(self.alive_members()):
                    rcode = self.assigned_roles[player.id]
                    if rcode == "phuthuy":
                        witch_members.append(player)
                        continue
                    if rcode in ["masoi", "soidau", "baove", "tientri", "cupid", "phongdan", "kedaomo"]:
                        res = await self.prompt_skill_for_role(player, rcode, wolf_bite_target_id=None)
                        if res:
                            if res.get("bite_id"):
                                wolf_votes.append(res["bite_id"])
                            if res.get("protect_id"):
                                protected_id = res["protect_id"]
                            if res.get("poison_id"):
                                witch_poison_id = res["poison_id"]

                bite_target = random.choice(wolf_votes) if wolf_votes else None

                for witch_player in witch_members:
                    if witch_player.id in self.alive_ids:
                        res = await self.prompt_skill_for_role(witch_player, "phuthuy", wolf_bite_target_id=bite_target)
                        if res and res.get("heal"):
                            witch_heal = True
                        if res and res.get("poison_id"):
                            witch_poison_id = res["poison_id"]

                sacrificed_ids = await self.handle_ducme_night_revive()

                night_deaths: set[int] = set(sacrificed_ids)
                if bite_target and bite_target != protected_id and not witch_heal:
                    if self.assigned_roles.get(bite_target) == "gialang" and not self.village_powers_disabled:
                        lives = self.gialang_lives.get(bite_target, 2)
                        if lives > 1:
                            self.gialang_lives[bite_target] = lives - 1
                        else:
                            night_deaths.update(self.mark_dead(bite_target))
                    else:
                        night_deaths.update(self.mark_dead(bite_target))

                if witch_poison_id:
                    night_deaths.update(self.mark_dead(witch_poison_id))

                # 2. BAN NGÀY - MỞ CHAT CHO NGƯỜI CÒN SỐNG
                await self.set_room_chat_permission(can_chat=True)
                if night_deaths:
                    names = [f"<@{uid}>" for uid in night_deaths]
                    await self.game_channel.send(f"☀️ **TRỜI SÁNG — ĐÊM QUA CÓ NGƯỜI CHẾT:** {', '.join(names)}")
                else:
                    await self.game_channel.send("☀️ **TRỜI SÁNG — ĐÊM QUA BÌNH YÊN, KHÔNG AI CHẾT!**")

                if await self.check_game_end():
                    return

                discuss_sec = timings["discuss"]
                await self.game_channel.send(f"💬 **THỜI GIAN THẢO LUẬN ({discuss_sec}s)** — Người còn sống có thể chat ngay bây giờ!")
                await asyncio.sleep(discuss_sec)

                # 3. BỎ PHIẾU TREO CỔ
                vote_sec = timings["vote"]
                alive_now = self.alive_members()
                vote_view = VoteView(alive_now, timeout=float(vote_sec))
                await self.game_channel.send(f"🗳️ **BỎ PHIẾU TREO CỔ ({vote_sec}s)** — Chọn người bạn nghi ngờ nhất:", view=vote_view)
                await vote_view.wait()

                tally: dict[int, int] = {}
                for target_uid in vote_view.votes.values():
                    if target_uid != -1:
                        tally[target_uid] = tally.get(target_uid, 0) + 1

                if tally:
                    top_uid, top_count = max(tally.items(), key=lambda x: x[1])
                    ties = [uid for uid, cnt in tally.items() if cnt == top_count]
                    if len(ties) == 1 and top_count >= 1:
                        accused = self.get_member(top_uid)
                        if accused:
                            savior = await self.handle_ducme_hanging_save(accused)
                            final_victim = savior or accused
                            r_code = self.assigned_roles[final_victim.id]

                            if r_code == "chanh":
                                await self.award_coins(
                                    winner_ids={final_victim.id},
                                    title="🤡 KẺ CHÁN ĐỜI CHIẾN THẮNG!",
                                    custom_message=f"🪢 {final_victim.mention} (**Kẻ Chán Đời**) đã bị treo cổ và giành chiến thắng!"
                                )
                                return

                            if r_code == "gialang":
                                self.village_powers_disabled = True
                                await self.game_channel.send("👴📜 **Già Làng** đã bị treo cổ! Toàn bộ Dân Làng mất hết kỹ năng.")

                            self.mark_dead(final_victim.id)
                            await self.game_channel.send(f"⚖️ **{final_victim.mention}** đã bị treo cổ!")
                    else:
                        await self.game_channel.send("⚖️ Phiếu bầu hòa nhau — không ai bị treo cổ hôm nay.")
                else:
                    await self.game_channel.send("⚖️ Không có phiếu bầu nào — không ai bị treo cổ hôm nay.")

                if await self.check_game_end():
                    return

        except asyncio.CancelledError:
            pass


class BanRoleModal(discord.ui.Modal, title="🚫 Ban / Gỡ Ban Role Ma Chó"):
    role_input = discord.ui.TextInput(
        label="Nhập mã role (VD: danthuong, kedaomo, ducme)",
        placeholder="Gõ mã role để ban hoặc gỡ ban nếu đã bị ban...",
        required=True,
        max_length=30
    )

    def __init__(self, game: WerewolfGame):
        super().__init__()
        self.game = game

    async def on_submit(self, interaction: discord.Interaction):
        code = self.role_input.value.strip().lower()
        if code not in ALL_WEREWOLF_ROLES:
            return await interaction.response.send_message(
                "❌ Mã role không tồn tại! Bấm **List Role** để xem mã chính xác.",
                ephemeral=True
            )
        if code == "masoi":
            return await interaction.response.send_message("🐺 Không thể ban **Sói**!", ephemeral=True)

        if code in self.game.banned_roles:
            self.game.banned_roles.remove(code)
            msg = f"✅ Đã **GỠ BAN** role {ALL_WEREWOLF_ROLES[code]['emoji']} **{ALL_WEREWOLF_ROLES[code]['name']}**."
        else:
            self.game.banned_roles.add(code)
            msg = f"🚫 Đã **BAN** role {ALL_WEREWOLF_ROLES[code]['emoji']} **{ALL_WEREWOLF_ROLES[code]['name']}**."

        if self.game.message:
            await self.game.message.edit(embed=self.game.build_embed())
        await interaction.response.send_message(msg, ephemeral=True)


class TimePresetSelect(discord.ui.Select):
    def __init__(self, game: WerewolfGame):
        self.game = game
        options = [
            discord.SelectOption(
                label=preset["label"],
                value=key,
                emoji=preset["emoji"],
                description=f"Đêm {preset['night']}s • Thảo luận {preset['discuss']}s • Vote {preset['vote']}s",
                default=(game.time_mode == key)
            )
            for key, preset in TIME_PRESETS.items()
        ]
        super().__init__(placeholder="⚙️ Chọn nhịp độ thời gian...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.game.host:
            return await interaction.response.send_message("❌ Chỉ chủ phòng mới đổi được thời gian!", ephemeral=True)
        if self.game.is_started:
            return await interaction.response.send_message("⚠️ Ván đã bắt đầu!", ephemeral=True)

        self.game.time_mode = self.values[0]
        preset = TIME_PRESETS[self.game.time_mode]
        await interaction.response.edit_message(embed=self.game.build_embed())
        await interaction.followup.send(f"✅ Đã chọn **{preset['emoji']} {preset['label']}**.", ephemeral=True)


class TimeSettingsView(discord.ui.View):
    def __init__(self, game: WerewolfGame):
        super().__init__(timeout=60.0)
        self.add_item(TimePresetSelect(game))


class LobbyView(discord.ui.View):
    def __init__(self, game: WerewolfGame):
        super().__init__(timeout=None)
        self.game = game

    @discord.ui.button(label="Tham Gia", emoji="✅", style=discord.ButtonStyle.success, row=0)
    async def join_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.game.is_started:
            return await interaction.response.send_message("Ván đã bắt đầu rồi!", ephemeral=True)
        if interaction.user in self.game.players:
            return await interaction.response.send_message("Bạn đã ở trong phòng rồi!", ephemeral=True)
        if len(self.game.players) >= 16:
            return await interaction.response.send_message("Phòng đã đủ 16 người!", ephemeral=True)

        self.game.players.append(interaction.user)
        await interaction.response.edit_message(embed=self.game.build_embed(), view=self)

    @discord.ui.button(label="Rời khỏi", emoji="✖️", style=discord.ButtonStyle.secondary, row=0)
    async def leave_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.game.is_started:
            return await interaction.response.send_message("Ván đang diễn ra, không thể rời!", ephemeral=True)
        if interaction.user == self.game.host:
            return await interaction.response.send_message("Chủ phòng hãy bấm **Hủy** để đóng phòng.", ephemeral=True)
        if interaction.user not in self.game.players:
            return await interaction.response.send_message("Bạn chưa tham gia phòng này.", ephemeral=True)

        self.game.players.remove(interaction.user)
        await interaction.response.edit_message(embed=self.game.build_embed(), view=self)

    @discord.ui.button(label="Hủy", style=discord.ButtonStyle.danger, row=0)
    async def cancel_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.game.host:
            return await interaction.response.send_message("Chỉ chủ phòng mới có thể hủy phòng!", ephemeral=True)

        active_guild_games.pop(self.game.guild_id, None)
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(content="🗑️ Phòng chờ Ma Chó đã được hủy.", view=self)

    @discord.ui.button(label="Bắt Đầu", emoji="🪄", style=discord.ButtonStyle.success, row=1)
    async def start_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.game.host:
            return await interaction.response.send_message("Chỉ chủ phòng mới có thể bắt đầu ván!", ephemeral=True)
        if len(self.game.players) < 3:
            return await interaction.response.send_message("Cần tối thiểu **3 người** để bắt đầu!", ephemeral=True)

        await interaction.response.defer()

        player_count = len(self.game.players)
        wolf_target = 1 if player_count <= 5 else (2 if player_count <= 9 else 3)

        wolf_pool_available = [r for r in ["soidau", "masoi"] if r not in self.game.banned_roles]
        if not wolf_pool_available:
            return await interaction.followup.send("❌ Toàn bộ role Sói đã bị ban!", ephemeral=True)

        pool = []
        while len(pool) < wolf_target:
            if "soidau" in wolf_pool_available and "soidau" not in pool:
                pool.append("soidau")
            elif "masoi" in wolf_pool_available:
                pool.append("masoi")
            else:
                pool.append(random.choice(wolf_pool_available))

        other_roles = [
            r for r in ALL_WEREWOLF_ROLES
            if r not in self.game.banned_roles
            and r not in ["masoi", "soidau"]
            and player_count >= ALL_WEREWOLF_ROLES[r].get("min_players", 0)
        ]

        while len(pool) < player_count:
            if "danthuong" not in self.game.banned_roles and len(pool) > len(other_roles):
                pool.append("danthuong")
            elif other_roles:
                pool.append(random.choice(other_roles))
            else:
                pool.append(random.choice(wolf_pool_available))

        random.shuffle(pool)
        self.game.alive_ids = {p.id for p in self.game.players}
        self.game.is_started = True

        room = await self.game.create_private_room()

        failed_dm = []
        for player, role_code in zip(self.game.players, pool):
            self.game.assigned_roles[player.id] = role_code
            if role_code == "gialang":
                self.game.gialang_lives[player.id] = 2
            if role_code == "phongdan":
                self.game.phongdan_cult_ids.add(player.id)

            role_info = ALL_WEREWOLF_ROLES[role_code]
            try:
                embed_dm = discord.Embed(
                    title=f"🎭 VAI TRÒ CỦA BẠN: {role_info['emoji']} {role_info['name'].upper()}",
                    description=(
                        f"**Phe:** {role_info['team'].upper()}\n"
                        f"**Kỹ năng:** {role_info['desc']}\n\n"
                        f"👉 Vào phòng chơi riêng: {room.mention}"
                    ),
                    color=discord.Color.dark_purple()
                )
                await player.send(embed=embed_dm)
            except discord.Forbidden:
                failed_dm.append(player.mention)

        mentions_all = " ".join([p.mention for p in self.game.players])
        intro_desc = (
            f"{mentions_all}\n\n"
            f"📩 Bot đã nhắn tin riêng (DM) báo role cho từng người.\n"
            f"🔒 Ban đêm kênh này sẽ tự động khóa chat; ban ngày chỉ người còn sống mới được chat."
        )
        if failed_dm:
            intro_desc += f"\n⚠️ Chưa gửi được DM cho: {', '.join(failed_dm)}."

        start_embed = discord.Embed(
            title="🐺 VÁN MA CHÓ BẮT ĐẦU!",
            description=intro_desc,
            color=discord.Color.gold()
        )
        await send_with_optional_image(room, start_embed, START_IMAGE_FILE)

        for item in self.children:
            item.disabled = True
        await interaction.message.edit(
            content=f"🌑 **Ván đấu đã bắt đầu tại:** {room.mention}",
            embed=self.game.build_embed(),
            view=self
        )

        self.game.loop_task = asyncio.create_task(self.game.run_game_loop())

    @discord.ui.button(label="Cài đặt", emoji="⚙️", style=discord.ButtonStyle.secondary, row=1)
    async def settings_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.game.host:
            return await interaction.response.send_message("❌ Chỉ chủ phòng mới chỉnh được Cài đặt!", ephemeral=True)
        if self.game.is_started:
            return await interaction.response.send_message("⚠️ Ván đã bắt đầu!", ephemeral=True)

        await interaction.response.send_message(
            "⚙️ Chọn nhịp độ thời gian:",
            view=TimeSettingsView(self.game),
            ephemeral=True
        )

    @discord.ui.button(label="List Role", emoji="📜", style=discord.ButtonStyle.secondary, row=2)
    async def list_role_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        lines = []
        for code, info in ALL_WEREWOLF_ROLES.items():
            status = "🚫 **[ĐÃ BAN]**" if code in self.game.banned_roles else "✅"
            lines.append(f"{status} {info['emoji']} **`{code}`** — {info['name']} ({info['team'].upper()}): {info['desc']}")

        embed = discord.Embed(
            title="📜 Danh Sách 13 Role Ma Chó",
            description="\n".join(lines)[:4000],
            color=discord.Color.blurple()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="Ban Role", emoji="🚫", style=discord.ButtonStyle.secondary, row=2)
    async def ban_role_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.game.host:
            return await interaction.response.send_message("Chỉ chủ phòng mới có thể Ban Role!", ephemeral=True)
        if self.game.is_started:
            return await interaction.response.send_message("Ván đã bắt đầu, không thể Ban Role!", ephemeral=True)

        await interaction.response.send_modal(BanRoleModal(self.game))

    @discord.ui.button(label="Hướng dẫn", emoji="📚", style=discord.ButtonStyle.secondary, row=2)
    async def guide_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        guide_text = (
            "1. Gõ `/macho` để mở phòng chờ (mỗi server chỉ mở được 1 phòng cùng lúc).\n"
            "2. Chủ phòng có thể chọn nhịp độ ở **Cài đặt**, xem **List Role**, cấm/mở role ở **Ban Role**.\n"
            "3. Bấm **Bắt Đầu**: bot nhắn DM báo role, tạo kênh riêng và `@` toàn bộ người chơi.\n"
            "4. Bot tự điều phối Đêm/Ngày/Vote và cộng **150 Coin** (thắng) / **50 Coin** (thua)."
        )
        await interaction.response.send_message(guide_text, ephemeral=True)


@bot.tree.command(name="macho", description="Mở bảng phòng chờ Mini Game Ma Chó (tối đa 1 phòng/server)")
async def slash_macho(interaction: discord.Interaction):
    if not interaction.guild or not isinstance(interaction.channel, discord.TextChannel):
        return await interaction.response.send_message("❌ Lệnh này chỉ dùng được trong kênh văn bản của server!", ephemeral=True)

    existing = active_guild_games.get(interaction.guild.id)
    if existing:
        where = existing.game_channel.mention if existing.game_channel else existing.lobby_channel.mention
        state = "đang diễn ra" if existing.is_started else "đang chờ người chơi"
        return await interaction.response.send_message(
            f"⚠️ Server hiện đã có 1 phòng Ma Chó **{state}** tại {where} (chủ phòng: {existing.host.mention}).",
            ephemeral=True
        )

    game = WerewolfGame(interaction.user, interaction.channel)
    active_guild_games[interaction.guild.id] = game
    view = LobbyView(game)

    if os.path.exists(BANNER_FILE):
        file = discord.File(BANNER_FILE, filename=BANNER_FILE)
        await interaction.response.send_message(embed=game.build_embed(), file=file, view=view)
    else:
        await interaction.response.send_message(embed=game.build_embed(), view=view)

    game.message = await interaction.original_response()


@bot.event
async def on_ready():
    await init_coin_db()
    print(f"✅ Bot đã sẵn sàng: {bot.user} (ID: {bot.user.id})")


TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(TOKEN)
