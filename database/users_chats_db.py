# Don't Remove Credit @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

import re
from pymongo.errors import DuplicateKeyError
import motor.motor_asyncio
from pymongo import MongoClient
from info import DATABASE_NAME, USER_DB_URI, OTHER_DB_URI, CUSTOM_FILE_CAPTION, IMDB, IMDB_TEMPLATE, MELCOW_NEW_USERS, BUTTON_MODE, SPELL_CHECK_REPLY, PROTECT_CONTENT, AUTO_DELETE, MAX_BTN, AUTO_FFILTER, SHORTLINK_API, SHORTLINK_URL, SHORTLINK_MODE, TUTORIAL, IS_TUTORIAL
import time
import datetime

my_client = MongoClient(OTHER_DB_URI)
mydb = my_client["referal_user"]

async def referal_add_user(user_id, ref_user_id):
    user_db = mydb[str(user_id)]
    user = {'_id': ref_user_id}
    try:
        user_db.insert_one(user)
        return True
    except DuplicateKeyError:
        return False
    

async def get_referal_all_users(user_id):
    user_db = mydb[str(user_id)]
    return user_db.find()
    
async def get_referal_users_count(user_id):
    user_db = mydb[str(user_id)]
    count = user_db.count_documents({})
    return count
    

async def delete_all_referal_users(user_id):
    user_db = mydb[str(user_id)]
    user_db.delete_many({}) 

default_setgs = {
    'button': BUTTON_MODE,
    'file_secure': PROTECT_CONTENT,
    'imdb': IMDB,
    'spell_check': SPELL_CHECK_REPLY,
    'welcome': MELCOW_NEW_USERS,
    'auto_delete': AUTO_DELETE,
    'auto_ffilter': AUTO_FFILTER,
    'max_btn': MAX_BTN,
    'template': IMDB_TEMPLATE,
    'caption': CUSTOM_FILE_CAPTION,
    'shortlink': SHORTLINK_URL,
    'shortlink_api': SHORTLINK_API,
    'is_shortlink': SHORTLINK_MODE,
    'fsub': None,
    'tutorial': TUTORIAL,
    'is_tutorial': IS_TUTORIAL
}


class Database:
    
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.users
        self.grp = self.db.groups
        self.users = self.db.uersz
        self.bot = self.db.clone_bots


    def new_user(self, id, name):
        return dict(
            id = id,
            name = name,
            file_id=None,
            caption=None,
            message_command=None,
            save=False,
            ban_status=dict(
                is_banned=False,
                ban_reason="",
            ),
        )


    def new_group(self, id, title):
        return dict(
            id = id,
            title = title,
            chat_status=dict(
                is_disabled=False,
                reason="",
            ),
            settings=default_setgs
        )
    
    async def add_user(self, id, name):
        user = self.new_user(id, name)
        await self.col.insert_one(user)
    
    async def is_user_exist(self, id):
        user = await self.col.find_one({'id':int(id)})
        return bool(user)
    
    async def total_users_count(self):
        count = await self.col.count_documents({})
        return count

    async def add_clone_bot(self, bot_id, user_id, bot_token):
        settings = {
            'bot_id': bot_id,
            'bot_token': bot_token,
            'user_id': user_id,
            'url': None,
            'api': None,
            'tutorial': None,
            'update_channel_link': None
        }
        await self.bot.insert_one(settings)

    async def is_clone_exist(self, user_id):
        clone = await self.bot.find_one({'user_id': int(user_id)})
        return bool(clone)

    async def delete_clone(self, user_id):
        await self.bot.delete_many({'user_id': int(user_id)})

    async def get_clone(self, user_id):
        clone_data = await self.bot.find_one({"user_id": user_id})
        return clone_data
            
    async def update_clone(self, user_id, user_data):
        await self.bot.update_one({"user_id": user_id}, {"$set": user_data}, upsert=True)

    async def get_bot(self, bot_id):
        bot_data = await self.bot.find_one({"bot_id": bot_id})
        return bot_data
            
    async def update_bot(self, bot_id, bot_data):
        await self.bot.update_one({"bot_id": bot_id}, {"$set": bot_data}, upsert=True)
    
    async def get_all_bots(self):
        return self.bot.find({})
        
    async def remove_ban(self, id):
        ban_status = dict(
            is_banned=False,
            ban_reason=''
        )
        await self.col.update_one({'id': id}, {'$set': {'ban_status': ban_status}})
    
    async def ban_user(self, user_id, ban_reason="No Reason"):
        ban_status = dict(
            is_banned=True,
            ban_reason=ban_reason
        )
        await self.col.update_one({'id': user_id}, {'$set': {'ban_status': ban_status}})

    async def get_ban_status(self, id):
        default = dict(
            is_banned=False,
            ban_reason=''
        )
        user = await self.col.find_one({'id':int(id)})
        if not user:
            return default
        return user.get('ban_status', default)

    async def get_all_users(self):
        return self.col.find({})
    

    async def delete_user(self, user_id):
        await self.col.delete_many({'id': int(user_id)})


    async def get_banned(self):
        users = self.col.find({'ban_status.is_banned': True})
        chats = self.grp.find({'chat_status.is_disabled': True})
        b_chats = [chat['id'] async for chat in chats]
        b_users = [user['id'] async for user in users]
        return b_users, b_chats
    


    async def add_chat(self, chat, title):
        chat = self.new_group(chat, title)
        await self.grp.insert_one(chat)
    

    async def get_chat(self, chat):
        chat = await self.grp.find_one({'id':int(chat)})

        expiry_time = datetime.datetime.now() + datetime.timedelta(seconds=seconds)
        user_data = {"id": user_id, "expiry_time": expiry_time, "has_free_trial": True}
        await self.users.update_one({"id": user_id}, {"$set": user_data}, upsert=True)
    
    
    async def all_premium_users(self):
        count = await self.users.count_documents({
        "expiry_time": {"$gt": datetime.datetime.now()}
        })
        return count

    async def set_thumbnail(self, id, file_id):
        await self.col.update_one({'id': int(id)}, {'$set': {'file_id': file_id}})

    async def get_thumbnail(self, id):
        user = await self.col.find_one({'id': int(id)})
        return user.get('file_id', None)

    async def set_caption(self, id, caption):
        await self.col.update_one({'id': int(id)}, {'$set': {'caption': caption}})

    async def get_caption(self, id):
        user = await self.col.find_one({'id': int(id)})
        return user.get('caption', None)

    async def set_msg_command(self, id, com):
        await self.col.update_one({'id': int(id)}, {'$set': {'message_command': com}})

    async def get_msg_command(self, id):
        user = await self.col.find_one({'id': int(id)})
        return user.get('message_command', None)

    async def set_save(self, id, save):
        await self.col.update_one({'id': int(id)}, {'$set': {'save': save}})

    async def get_save(self, id):

                   (user_id, action, timestamp))

    conn.commit()
    conn.close()

        self.cursor.execute("SELECT chat_id FROM banned_chats")
        banned_chats = [row[0] for row in self.cursor.fetchall()]

        return banned_users, banned_chats
# Don't Remove Credit @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on Telegram @KingVJ01

import re
import motor.motor_asyncio
import sqlite3
import datetime
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from info import DATABASE_NAME, USER_DB_URI, OTHER_DB_URI, CUSTOM_FILE_CAPTION, IMDB, IMDB_TEMPLATE, MELCOW_NEW_USERS, BUTTON_MODE, SPELL_CHECK_REPLY, PROTECT_CONTENT, AUTO_DELETE, MAX_BTN, AUTO_FFILTER, SHORTLINK_API, SHORTLINK_URL, SHORTLINK_MODE, TUTORIAL, IS_TUTORIAL

# 🔹 MongoDB Connection
my_client = MongoClient(OTHER_DB_URI)
mydb = my_client["referal_user"]

# 🔹 MongoDB-Based Database Class
class MongoDatabase:
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.users
        self.grp = self.db.groups
        self.users = self.db.uersz
        self.bot = self.db.clone_bots

    async def is_user_exist(self, user_id):
        """Check if a user exists in the database."""
        user = await self.col.find_one({'id': int(user_id)})
        return bool(user)

    async def get_settings(self, chat_id):
        """Retrieve chat settings from the database."""
        chat = await self.grp.find_one({'id': int(chat_id)})
        return chat.get('settings', default_setgs) if chat else default_setgs

    async def set_welcome_message(self, chat_id, welcome_msg):
        """Store a custom welcome message for a chat."""
        await self.grp.update_one({'id': int(chat_id)}, {"$set": {"welcome": welcome_msg}}, upsert=True)

# 🔹 SQLite-Based Database Class
class SQLiteDatabase:
    def __init__(self, db_path="bot_database.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS warnings (
                user_id INTEGER PRIMARY KEY,
                chat_id INTEGER,
                count INTEGER DEFAULT 0
            )"""
        )
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS banned_users (
                user_id INTEGER PRIMARY KEY
            )"""
        )
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS banned_chats (
                chat_id INTEGER PRIMARY KEY
            )"""
        )
        self.conn.commit()

    async def get_banned(self):
        """Retrieve banned users and chats from the database."""
        self.cursor.execute("SELECT user_id FROM banned_users")
        banned_users = [row[0] for row in self.cursor.fetchall()]

        self.cursor.execute("SELECT chat_id FROM banned_chats")
        banned_chats = [row[0] for row in self.cursor.fetchall()]

        return banned_users, banned_chats

    async def get_warnings(self, chat_id, user_id):
        """Retrieve the number of warnings for a specific user in a chat."""
        self.cursor.execute("SELECT count FROM warnings WHERE chat_id = ? AND user_id = ?", (chat_id, user_id))
        result = self.cursor.fetchone()
        return result[0] if result else 0

    async def add_warning(self, chat_id, user_id):
        """Increase the warning count for a user."""
        current_warnings = await self.get_warnings(chat_id, user_id)
        if current_warnings == 0:
            self.cursor.execute("INSERT INTO warnings (chat_id, user_id, count) VALUES (?, ?, 1)", (chat_id, user_id))
        else:
            self.cursor.execute("UPDATE warnings SET count = count + 1 WHERE chat_id = ? AND user_id = ?", (chat_id, user_id))
        self.conn.commit()

    async def reset_warnings(self, chat_id, user_id):
        """Reset warnings for a user."""
        self.cursor.execute("DELETE FROM warnings WHERE chat_id = ? AND user_id = ?", (chat_id, user_id))
        self.conn.commit()

# 🔹 Initialize Database Instances
mongo_db = MongoDatabase(USER_DB_URI, DATABASE_NAME)
sqlite_db = SQLiteDatabase()
