from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _
from django.views.generic.list import ListView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from misc.models import File
from misc.s3 import S3
from misc.serializers import FileSerializer
from users.mixins import AdminPermMixin, LoginRequiredMixin

from .models import Notification


class FileView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, id, uuid):
        file = get_object_or_404(File, uuid=uuid, id=id)
        url = file.get_url()
        return Response(url)

    def post(self, request):
        try:
            ext = ""
            if len(request.data["name"].split(".")) > 1:
                ext = request.data["name"].split(".")[-1]
            print("ext: ", ext)

            serializer = FileSerializer(
                data={
                    "name": request.data["name"],
                    "ext": ext,
                }
            )
            serializer.is_valid(raise_exception=True)
            f = serializer.save()
            key = (
                f"{f.id}-{serializer.data['name'].split('.')[0]}/{serializer.data['name']}"
            )
            print("key:", key)
            print("full_key:", S3().get_presigned_url(key))
            f.key = key
            f.save()
            # Specifics based on Editor.js expectations
            return Response(
                {
                    "success": 1,
                    "file": {
                        "url": S3().get_presigned_url(key),
                        "id": f.id,
                        "name": f.name,
                        "ext": f.ext,
                        "get_url": f.get_url(),
                        "size": None,
                        "title": f.name,
                    },
                }
            )
        except Exception as e:
            print(str(e))
            return {}

    def delete(self, request, id):
        if request.user.is_admin_or_manager:
            file = get_object_or_404(File, pk=id)
            file.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class NotificationListView(LoginRequiredMixin, AdminPermMixin, ListView):
    template_name = "notifications.html"
    queryset = Notification.objects.all()
    paginate_by = 40

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Notifications")
        context["subtitle"] = _("global")
        return context
