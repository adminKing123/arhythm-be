from django.http import FileResponse, Http404, HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from config import CONFIG
import json
from utils import get_database_as_dict

class DownloadDBView(APIView):
    def get(self, request, *args, **kwargs):
        # grab query param
        key = request.query_params.get("admin_actions_secret_key")
        as_filename = request.query_params.get("as_filename", "db.sqlite3")
        
        if key != CONFIG["ADMIN_ACTIONS_SECRET_KEY"]:
            return Response({"detail": "Unauthorized"}, status=403)

        file_path = "db.sqlite3"
        try:
            return FileResponse(open(file_path, "rb"), as_attachment=True, filename=as_filename)
        except FileNotFoundError:
            raise Http404("File not found")

class DownloadDBJsonView(APIView):
    """
    Export the database to JSON and download it.

    The JSON is generated directly from the database
    using get_database_as_dict().
    """

    def get(self, request, *args, **kwargs):
        # Grab query param
        key = request.query_params.get(
            "admin_actions_secret_key"
        )

        as_filename = request.query_params.get(
            "as_filename",
            "db.json",
        )

        # Check secret key
        if key != CONFIG["ADMIN_ACTIONS_SECRET_KEY"]:
            return Response(
                {"detail": "Unauthorized"},
                status=403,
            )

        # Get database data as Python dict
        data = get_database_as_dict()

        # Convert dict to JSON
        json_data = json.dumps(
            data,
            ensure_ascii=False,
            indent=4,
        )

        # Return JSON as downloadable file
        response = HttpResponse(
            json_data,
            content_type="application/json; charset=utf-8",
        )

        response["Content-Disposition"] = (
            f'attachment; filename="{as_filename}"'
        )

        return response