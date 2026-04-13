from dotenv import load_dotenv
import os
from supabase import create_client

# load env variables
load_dotenv()

# get values
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# create client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def test_connection():
    try:
        response = supabase.table("articles_raw").select("id").limit(1).execute()
        print("✅ DB Connected Successfully")
        print("Response:", response.data)
    except Exception as e:
        print("❌ DB Connection Failed")
        print("Error:", e)


def insert_test():
    try:
        response = supabase.table("articles_raw").insert({
            "title": "Test Article",
            "content": "This is a test article",
            "url": "https://test.com/article1",
            "source": "test",
            "content_hash": "test_hash_123"
        }).execute()

        print("✅ Insert Successful")
        print(response.data)
    except Exception as e:
        print("❌ Insert Failed:", e)


def fetch_test():
    try:
        response = supabase.table("articles_raw").select("*").limit(5).execute()
        print("✅ Fetch Successful")
        for row in response.data:
            print(row)
    except Exception as e:
        print("❌ Fetch Failed:", e)


if __name__ == "__main__":
    test_connection()
    insert_test()
    fetch_test()