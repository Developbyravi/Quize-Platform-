import asyncio
import httpx
import time
import sys

BASE_URL = "http://127.0.0.1:8001/api"
sem = asyncio.Semaphore(20)

async def simulate_participant(participant_id: int):
    async with sem:
        email = f"user{participant_id}@engday.edu"
        prn = f"PRN{participant_id:04d}"
        mobile = f"900000{participant_id:04d}"

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                # 1. Register / Login
                reg_payload = {
                    "full_name": f"Student {participant_id}",
                    "email": email,
                    "mobile_number": mobile,
                    "college_name": "College of Engineering",
                    "department": "CSE",
                    "year": "TE",
                    "prn_student_id": prn,
                    "password": "password123"
                }
                res = await client.post(f"{BASE_URL}/auth/register", json=reg_payload)
                if res.status_code == 201:
                    token = res.json()["access_token"]
                else:
                    login_res = await client.post(f"{BASE_URL}/auth/login", json={"email": email, "password": "password123"})
                    token = login_res.json()["access_token"]

                headers = {"Authorization": f"Bearer {token}"}

                # 2. Enter Round 1
                await client.post(f"{BASE_URL}/rounds/1/start", headers=headers)

                # 3. Answer MCQs
                for q_id in range(1, 4):
                    await client.post(f"{BASE_URL}/quiz/1/answer", headers=headers, json={
                        "question_id": q_id,
                        "selected_option": "B",
                        "is_marked_for_review": False
                    })

                # 4. Draft Autosave Round 2
                await client.post(f"{BASE_URL}/code/autosave", headers=headers, json={
                    "question_id": 21,
                    "round_id": 2,
                    "code": "def solve(arr): return sum(arr)",
                    "language": "python"
                })

                # 5. Fetch Leaderboard
                await client.get(f"{BASE_URL}/leaderboard", headers=headers)

                if participant_id % 20 == 0:
                    print(f"[{participant_id}/100] User journey completed successfully...", flush=True)

                return True
            except Exception as e:
                print(f"[{participant_id}/100] Error: {e}", flush=True)
                return False

async def main():
    print("=" * 60, flush=True)
    print("STARTING SIMULATED LOAD TEST FOR 100 PARTICIPANTS", flush=True)
    print("=" * 60, flush=True)
    
    start_time = time.time()
    tasks = [simulate_participant(i) for i in range(1, 101)]
    results = await asyncio.gather(*tasks)
    
    elapsed = time.time() - start_time
    successful = sum(1 for r in results if r)
    
    print("-" * 60, flush=True)
    print(f"Total Participants Simulated: {len(results)}", flush=True)
    print(f"Successful User Journeys    : {successful}", flush=True)
    print(f"Failed User Journeys        : {len(results) - successful}", flush=True)
    print(f"Total Time Taken            : {elapsed:.2f} seconds", flush=True)
    print(f"Average Throughput          : {len(results) / elapsed:.2f} journeys/sec", flush=True)
    print("=" * 60, flush=True)

if __name__ == "__main__":
    asyncio.run(main())
