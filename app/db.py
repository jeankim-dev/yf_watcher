import aiosqlite

DB_PATH = "results.db"


async def save_result(result: dict):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS screening_results (
                symbol TEXT,
                rsi REAL,
                macd REAL
            )
        """)
        await db.execute(
            "INSERT INTO screening_results VALUES (?, ?, ?)",
            (result["symbol"], result["rsi"], result["macd"])
        )
        await db.commit()
