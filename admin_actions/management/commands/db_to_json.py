import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from utils import get_database_as_dict

class Command(BaseCommand):
    help = "Export database data to JSON while preserving IDs and relationships"

    def handle(self, *args, **options):
        output_dir = (
            Path(settings.BASE_DIR) / "database_export"
        )

        output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_file = output_dir / "db.json"
        data = get_database_as_dict()

        with open(
            output_file,
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                data,
                file,
                ensure_ascii=False,
                indent=4,
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Database exported successfully to:\n"
                f"{output_file}"
            )
        )

        self.stdout.write(
            f"Actors: {len(data['actors'])}"
        )

        self.stdout.write(
            f"Artists: {len(data['artists'])}"
        )

        self.stdout.write(
            f"Languages: {len(data['languages'])}"
        )

        self.stdout.write(
            f"Albums: {len(data['albums'])}"
        )

        self.stdout.write(
            f"Songs: {len(data['songs'])}"
        )