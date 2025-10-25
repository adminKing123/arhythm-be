from django.http import FileResponse, Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from config import CONFIG

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
