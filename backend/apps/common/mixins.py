from rest_framework.exceptions import PermissionDenied

class SchoolFilterMixin:
    def get_school(self):
        school = getattr(self.request, 'school', None)
        if not school and hasattr(self.request, 'user') and self.request.user.is_authenticated:
            school = getattr(self.request.user, 'school', None)
        return school

    def get_queryset(self):
        queryset = super().get_queryset()
        school = self.get_school()
        if school:
            if hasattr(queryset.model, 'school'):
                queryset = queryset.filter(school=school)
            else:
                raise PermissionDenied(
                    f"Model {queryset.model.__name__} does not have a 'school' field."
                )
        else:
            queryset = queryset.none()
        return queryset

    def perform_create(self, serializer):
        school = self.get_school()
        if school:
            if hasattr(serializer.Meta.model, 'school'):
                serializer.save(school=school)
            else:
                serializer.save()
        else:
            raise PermissionDenied("School not set. Please ensure you are authenticated and belong to a school.")

    def perform_update(self, serializer):
        # Prevent changing the school of an existing record (optional)
        # We don't need to do anything special here because the school field is not updatable via the serializer.
        serializer.save()