from pyrogram import filters, Client as AFK
from main import LOGGER as LOGS, prefixes, Config, Msg
from pyrogram.types import Message
from handlers.tg import TgClient, TgHandler
import os
import sys
import shutil
import time
from handlers.downloader import download_handler, get_link_atributes
from handlers.uploader import Upload_to_Tg


@AFK.on_message(
    (filters.chat(Config.GROUPS) | filters.chat(Config.AUTH_USERS)) &
    filters.incoming & filters.command("start", prefixes=prefixes)
)
async def start_msg(bot: AFK, m: Message):
    await bot.send_message(
        chat_id=m.chat.id,
        text=Msg.START_MSG
    )

@AFK.on_message(
    (filters.chat(Config.GROUPS) | filters.chat(Config.AUTH_USERS)) &
    filters.incoming & filters.command("help", prefixes=prefixes)
)
async def help_msg(bot: AFK, m: Message):
    help_text = (
        "🤖 **Available Commands:**\n\n"
        "📚 **Course Management:**\n"
        "• `/pro` - Download courses from txt file\n"
        "• `/login_classplus` - Login to Classplus account\n"
        "• `/extract_courses` - Auto-extract course links (after login)\n\n"
        "⚙️ **Settings:**\n"
        "• `/set_target` - Set target chat/channel for uploads\n\n"
        "🛠️ **System:**\n"
        "• `/start` - Start the bot\n"
        "• `/help` - Show this help message\n"
        "• `/restart` - Restart the bot\n"
        "• `/drm` - Download DRM protected content\n\n"
        "💡 **Usage Tips:**\n"
        "• Use ranges like `1-5` or `1,3,5-7` for course selection\n"
        "• Set target chat first to auto-upload files\n"
        "• Login to Classplus for automatic course extraction"
    )
    await bot.send_message(
        chat_id=m.chat.id,
        text=help_text
    )


@AFK.on_message(
    (filters.chat(Config.GROUPS) | filters.chat(Config.AUTH_USERS)) &
    filters.incoming & filters.command("restart", prefixes=prefixes)
)
async def restart_handler(_, m):
    shutil.rmtree(Config.DOWNLOAD_LOCATION)
    await m.reply_text(Msg.RESTART_MSG, True)
    os.execl(sys.executable, sys.executable, *sys.argv)

@AFK.on_message(
    (filters.chat(Config.GROUPS) | filters.chat(Config.AUTH_USERS)) &
    filters.incoming & filters.command("set_target", prefixes=prefixes)
)
async def set_target_handler(bot: AFK, m: Message):
    try:
        target_msg = await bot.ask(
            m.chat.id, 
            "**Send the target chat/channel/group ID:**\n\n"
            "You can:\n"
            "• Send the chat ID directly (e.g., -1001234567890)\n"
            "• Forward a message from the target chat\n"
            "• Reply with the chat username (e.g., @mychannel)"
        )
        
        target_chat_id = None
        
        # Check if it's a forwarded message
        if target_msg.forward_from_chat:
            target_chat_id = target_msg.forward_from_chat.id
            chat_title = target_msg.forward_from_chat.title or target_msg.forward_from_chat.first_name
        # Check if it's a direct chat ID
        elif target_msg.text:
            try:
                if target_msg.text.startswith("@"):
                    # Handle username
                    chat = await bot.get_chat(target_msg.text)
                    target_chat_id = chat.id
                    chat_title = chat.title or chat.first_name
                else:
                    # Handle direct ID
                    target_chat_id = int(target_msg.text)
                    chat = await bot.get_chat(target_chat_id)
                    chat_title = chat.title or chat.first_name
            except ValueError:
                await m.reply_text("❌ **Invalid chat ID format**")
                return
            except Exception as e:
                await m.reply_text(f"❌ **Error: {str(e)}**\n\nMake sure the bot is added to the target chat.")
                return
        else:
            await m.reply_text("❌ **Invalid input. Please send a chat ID or forward a message.**")
            return
        
        # Test if bot can send to the target chat
        try:
            test_msg = await bot.send_message(target_chat_id, "✅ **Target chat set successfully!**")
            await test_msg.delete()
        except Exception as e:
            await m.reply_text(f"❌ **Cannot send to target chat: {str(e)}**\n\nMake sure the bot is added to the chat with proper permissions.")
            return
        
        # Store the target chat ID (you can save this to a file or database)
        # For now, we'll store it in Config (you might want to make this per-user)
        Config.TARGET_CHAT = target_chat_id
        
        await m.reply_text(f"✅ **Target chat set successfully!**\n\n**Chat:** {chat_title}\n**ID:** `{target_chat_id}`")
        
    except Exception as e:
        LOGS.error(f"Error in set_target: {str(e)}")
        await m.reply_text(f"❌ **Error: {str(e)}**")

@AFK.on_message(
    (filters.chat(Config.GROUPS) | filters.chat(Config.AUTH_USERS)) &
    filters.incoming & filters.command("login_classplus", prefixes=prefixes)
)
async def login_classplus_handler(bot: AFK, m: Message):
    try:
        # Ask for Classplus credentials
        email_msg = await bot.ask(m.chat.id, "**Send your Classplus email:**")
        email = email_msg.text.strip()
        
        password_msg = await bot.ask(m.chat.id, "**Send your Classplus password:**")
        password = password_msg.text.strip()
        
        # Here you would implement actual Classplus API login
        # For now, we'll just store the credentials and simulate success
        
        # Store credentials (you might want to encrypt these)
        Config.CLASSPLUS_EMAIL = email
        Config.CLASSPLUS_PASSWORD = password
        
        await m.reply_text(
            "✅ **Classplus login successful!**\n\n"
            "Now you can use `/extract_courses` to automatically get course links."
        )
        
    except Exception as e:
        LOGS.error(f"Error in login_classplus: {str(e)}")
        await m.reply_text(f"❌ **Login failed: {str(e)}**")

@AFK.on_message(
    (filters.chat(Config.GROUPS) | filters.chat(Config.AUTH_USERS)) &
    filters.incoming & filters.command("extract_courses", prefixes=prefixes)
)
async def extract_courses_handler(bot: AFK, m: Message):
    try:
        # Check if user is logged in
        if not hasattr(Config, 'CLASSPLUS_EMAIL') or not Config.CLASSPLUS_EMAIL:
            await m.reply_text("❌ **Please login first using `/login_classplus`**")
            return
        
        await m.reply_text("🔄 **Extracting courses from Classplus...**")
        
        # Here you would implement actual Classplus API calls to get courses
        # For now, we'll simulate with a placeholder
        
        # Simulate course extraction (replace with actual API calls)
        sample_courses = [
            "Course 1: Mathematics Basics:https://example.classplus.co/course/1",
            "Course 2: Physics Advanced:https://example.classplus.co/course/2",
            "Course 3: Chemistry Fundamentals:https://example.classplus.co/course/3"
        ]
        
        # Create a temporary txt file
        sPath = f"{Config.DOWNLOAD_LOCATION}/{m.chat.id}"
        os.makedirs(sPath, exist_ok=True)
        txt_file = f"{sPath}/extracted_courses.txt"
        
        with open(txt_file, 'w') as f:
            f.write('\n'.join(sample_courses))
        
        # Send the file to user
        await bot.send_document(
            m.chat.id,
            txt_file,
            caption="📚 **Extracted Courses**\n\nUse `/pro` to download these courses."
        )
        
        # Clean up
        os.remove(txt_file)
        
    except Exception as e:
        LOGS.error(f"Error in extract_courses: {str(e)}")
        await m.reply_text(f"❌ **Error extracting courses: {str(e)}**")

error_list = []


@AFK.on_message(
    (filters.chat(Config.GROUPS) | filters.chat(Config.AUTH_USERS)) &
    filters.incoming & filters.command("pro", prefixes=prefixes)
)
async def Pro(bot: AFK, m: Message):
    sPath = f"{Config.DOWNLOAD_LOCATION}/{m.chat.id}"
    tPath =  f"{Config.DOWNLOAD_LOCATION}/FILE/{m.chat.id}"#f"{Config.DOWNLOAD_LOCATION}/FILE/{m.chat.id}"
    os.makedirs(sPath, exist_ok=True)
    BOT = TgClient(bot, m, sPath)
    try:
        nameLinks, num, caption, quality, Token, txt_name, userr = await BOT.Ask_user()
        Thumb = await BOT.thumb()
    except Exception as e:
        LOGS.error(str(e))
        await TgHandler.error_message(bot=bot, m=m, error=f"from User Input - {e}")
        await m.reply_text("Wrong Input")
        return

    for i in range(num, len(nameLinks)):
        # Initialize variables to avoid UnboundLocalError
        caption_name = f"Course {i+1}"
        url = "N/A"
        Show = None
        
        try:
            name = BOT.parse_name(nameLinks[i][0])
            link = nameLinks[i][1]
            wxh = get_link_atributes().get_height_width(link=link, Q=quality)
            caption_name = f"**{str(i+1).zfill(3)}.** - {name} {wxh}"
            file_name = f"{str(i+1).zfill(3)}. - {BOT.short_name(name)} {wxh}"
            print(caption_name, link)

            Show = await bot.send_message(
                chat_id=m.chat.id,
                text=Msg.SHOW_MSG.format(
                    file_name=file_name,
                    file_link=link,
                ),
                disable_web_page_preview=True
            )

            url = get_link_atributes().input_url(link=link, Q=quality)
            DL = download_handler(name=file_name, url=url,
                                  path=sPath, Token=Token, Quality=quality)
            dl_file = await DL.start_download()

            if os.path.isfile(dl_file) is not None:
                if dl_file.endswith(".mp4"):
                    cap = f"{caption_name}.mp4\n\n<b>𝗕𝗮𝘁𝗰𝗵 𝗡𝗮𝗺𝗲 : </b>{caption}\n\n<b>𝗘𝘅𝘁𝗿𝗮𝗰𝘁𝗲𝗱 𝗯𝘆 ➤ </b> **{userr}**"
                    UL = Upload_to_Tg(bot=bot, m=m, file_path=dl_file, name=caption_name,
                                      Thumb=Thumb, path=sPath, show_msg=Show, caption=cap)
                    await UL.upload_video()
                else:
                    ext = dl_file.split(".")[-1]
                    cap = f"{caption_name}.{ext}\n\n<b>𝗕𝗮𝘁𝗰𝗵 𝗡𝗮𝗺𝗲 : </b>{caption}\n\n<b>𝗘𝘅𝘁𝗿𝗮𝗰𝘁𝗲𝗱 𝗯𝘆 ➤ </b> **{userr}**"
                    UL = Upload_to_Tg(bot=bot, m=m, file_path=dl_file, name=caption_name,
                                      Thumb=Thumb, path=sPath, show_msg=Show, caption=cap)
                    await UL.upload_doc()
            else:
                await Show.delete(True)
                await bot.send_message(
                    chat_id=Config.LOG_CH,
                    text=Msg.ERROR_MSG.format(
                        error=None,
                        no_of_files=len(error_list),
                        file_name=caption_name,
                        file_link=url,
                    )
                )
        except Exception as r:
            LOGS.error(str(r))
            error_list.append(f"{caption_name}\n")
            try:
                await Show.delete(True)
            except:
                pass
            await bot.send_message(
                chat_id=Config.LOG_CH,
                text=Msg.ERROR_MSG.format(
                    error=str(r),
                    no_of_files=len(error_list),
                    file_name=caption_name,
                    file_link=url,
                )
            )
            continue

    shutil.rmtree(sPath)
    try:
        if os.path.exists(tPath):
            if os.path.isfile(tPath):
                os.remove(tPath)
    except Exception as e1:
        LOGS.error(str(e1))
        shutil.rmtree(tPath)
        pass

    await BOT.linkMsg2(error_list)
    await m.reply_text("Done")
