from rest_framework import viewsets
from .models import AcademicYear, Term, Class, Stream, Subject
from .serializers import (
    AcademicYearSerializer, TermSerializer, ClassSerializer,
    StreamSerializer, SubjectSerializer
)
from apps.common.mixins import SchoolFilterMixin
from apps.accounts.permissions import IsAdmin, IsBursar, IsPrincipal

class AcademicYearViewSet(SchoolFilterMixin, viewsets.ModelViewSet):
    queryset = AcademicYear.objects.all()
    serializer_class = AcademicYearSerializer
    permission_classes = [IsAdmin | IsBursar | IsPrincipal]

class TermViewSet(SchoolFilterMixin, viewsets.ModelViewSet):
    queryset = Term.objects.all()
    serializer_class = TermSerializer
    permission_classes = [IsAdmin | IsBursar | IsPrincipal]

class ClassViewSet(SchoolFilterMixin, viewsets.ModelViewSet):
    queryset = Class.objects.all()
    serializer_class = ClassSerializer
    permission_classes = [IsAdmin | IsBursar | IsPrincipal]

class StreamViewSet(SchoolFilterMixin, viewsets.ModelViewSet):
    queryset = Stream.objects.all()
    serializer_class = StreamSerializer
    permission_classes = [IsAdmin | IsBursar | IsPrincipal]

class SubjectViewSet(SchoolFilterMixin, viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [IsAdmin | IsBursar | IsPrincipal]