import os
import shutil
import subprocess
import zipfile
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

TOKEN = "8119878959:AAGZdBTiBfgq34ZOp5Qsobfh3zU0cgXQAQg"
DOWNLOAD_BASE = "downloaded_sites"

def zip_folder(folder_path, zip_path):
    shutil.make_archive(zip_path.replace('.zip',''), 'zip', folder_path)

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "سلام! آدرس سایت رو با دستور زیر بفرست تا کل قالب سایت رو برات دانلود کنم و ارسال کنم:\n\n"
        "/download https://example.com"
    )

def download_command(update: Update, context: CallbackContext):
    if len(context.args) != 1:
        update.message.reply_text("لطفا یک آدرس سایت معتبر وارد کن:\nمثال:\n/download https://example.com")
        return

    url = context.args[0]
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id

    update.message.reply_text(f"در حال دانلود کامل سایت {url} ... لطفا صبر کن.")

    safe_name = url.replace("://", "_").replace("/", "_")
    download_path = os.path.join(DOWNLOAD_BASE, safe_name)

    if os.path.exists(download_path):
        shutil.rmtree(download_path)
    os.makedirs(download_path, exist_ok=True)

    command = [
        "wget",
        "--mirror",
        "--convert-links",
        "--adjust-extension",
        "--no-parent",
        "--quiet",
        "-P", download_path,
        url
    ]

    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        update.message.reply_text(f"خطا در دانلود سایت: {e}")
        return

    zip_file_path = download_path + ".zip"
    if os.path.exists(zip_file_path):
        os.remove(zip_file_path)
    zip_folder(download_path, download_path)

    try:
        with open(zip_file_path, 'rb') as f:
            update.message.reply_document(document=f, filename=os.path.basename(zip_file_path))
        update.message.reply_text("دانلود و ارسال قالب سایت انجام شد.")
    except Exception as e:
        update.message.reply_text(f"خطا در ارسال فایل: {e}")

    try:
        shutil.rmtree(download_path)
        os.remove(zip_file_path)
    except Exception:
        pass

def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("download", download_command))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    if not os.path.exists(DOWNLOAD_BASE):
        os.makedirs(DOWNLOAD_BASE)
    main()
