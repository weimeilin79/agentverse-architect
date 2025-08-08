import os
import sqlalchemy
from google.cloud.sql.connector import Connector

def setup_database():
    """Connects to the Cloud SQL DB, creates tables, and inserts data."""
    try:
        # --- Environment variables read from the setup.sh script ---
        project_id = os.environ["GCP_PROJECT_ID"]
        region = os.environ["GCP_REGION"]
        instance_name = os.environ["DB_INSTANCE_NAME"]
        db_name = os.environ["DB_NAME"]
        db_user = os.environ["DB_USER"]
        db_pass = os.environ["DB_PASSWORD"]

        instance_connection_name = f"{project_id}:{region}:{instance_name}"

        print(f"Connecting to instance: {instance_connection_name}")

        connector = Connector()

        def getconn():
            conn = connector.connect(
                instance_connection_name,
                "pg8000",
                user=db_user,
                password=db_pass,
                db=db_name
            )
            return conn

        pool = sqlalchemy.create_engine(
            "postgresql+pg8000://",
            creator=getconn,
        )

        with pool.connect() as db_conn:
            print("Connection successful. Creating table and inserting data...")
            # Create the abilities table
            db_conn.execute(sqlalchemy.text(
                """
                CREATE TABLE IF NOT EXISTS abilities (
                    id SERIAL PRIMARY KEY,
                    familiar_name VARCHAR(50) NOT NULL,
                    ability_name VARCHAR(50) UNIQUE NOT NULL,
                    damage_points INTEGER NOT NULL,
                    element VARCHAR(20) NOT NULL
                );
                """
            ))
            db_conn.commit()

            # Clear existing data to make script idempotent
            db_conn.execute(sqlalchemy.text("TRUNCATE TABLE abilities;"))
            db_conn.commit()

            # Insert lore-based data
            abilities_to_insert = [
                # Fire Elemental Abilities
                {"familiar": "Fire Elemental", "ability": "inferno_lash", "damage": 85, "element": "Fire"},
                {"familiar": "Fire Elemental", "ability": "emberstorm", "damage": 90, "element": "Fire"}, 
                {"familiar": "Fire Elemental", "ability": "Pyroclasm", "damage": 80, "element": "Fire"}, 
            ]

            for ability in abilities_to_insert:
                 stmt = sqlalchemy.text(
                    """
                    INSERT INTO abilities (familiar_name, ability_name, damage_points, element)
                    VALUES (:familiar, :ability, :damage, :element)
                    ON CONFLICT (ability_name) DO NOTHING;
                    """
                )
                 db_conn.execute(stmt, parameters=ability)

            db_conn.commit()
            print("Database setup complete. 'abilities' table created and populated.")

            # Verify insertion
            results = db_conn.execute(sqlalchemy.text("SELECT * FROM abilities;")).fetchall()
            print("\n--- Verifying Inserted Data ---")
            for row in results:
                print(row)
            print("-----------------------------")


    except Exception as e:
        print(f"An error occurred: {e}")
        exit(1)

if __name__ == "__main__":
    setup_database()