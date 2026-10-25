import argparse
import logging

from sqlalchemy import create_engine

from src.config import get_db_url
from src.extract import extract_all

def main() -> None:
    parse = argparse.ArgumentParser(description= "Pokémon ETL pipeline")
    parse.add_argument("--generations", type=int, nargs="+", default=[1], 
                       help="Generations to retrieve, e.g., --generations 1 2 3")
    parse.add_argument("--refresh", action="store_true", 
                       help="Bypass cache, re-call the API")
    args = parse.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    engine = create_engine(get_db_url())
    counts = extract_all(engine, args.generations, args.refresh)
    logging.info("Extract complete: %s", dict(counts))

if __name__ == "__main__":
    main()