from rest_framework.exceptions import PermissionDenied

class SchoolFilterMixin:
    """
    Automatically filters queryset by the current school (from request.school)
    and sets school on create/update.
    """
    def get_queryset(self):
        queryset = super().get_queryset()
        school = getattr(self.request, 'school', None)
        if school:
            # If the model has a 'school' field, filter by it
            if hasattr(queryset.model, 'school'):
                queryset = queryset.filter(school=school)
            else:
                # If the model doesn't have a school field, raise an error to prevent accidental data leakage
                # You can override this method in the child viewset if you need custom filtering.
                raise PermissionDenied(
                    f"Model {queryset.model.__name__} does not have a 'school' field. "
                    "Add a school field or override get_queryset to filter by school manually."
                )
        else:
            # No school in request – return empty queryset for protected endpoints
            # (unless the viewset overrides this behavior)
            queryset = queryset.none()
        return queryset

    def perform_create(self, serializer):
        school = getattr(self.request, 'school', None)
        if school:
            # If the model has a 'school' field, set it
            if hasattr(serializer.Meta.model, 'school'):
                serializer.save(school=school)
            else:
                # If no school field, just save normally (but this should be avoided)
                serializer.save()
        else:
            # For public endpoints, allow creation without school (e.g., school registration)
            # This should only be used for views that are explicitly public.
            serializer.save()

    def perform_update(self, serializer):
        # Prevent changing the school of an existing record (optional)
        # We don't need to do anything special here because the school field is not updatable via the serializer.
        serializer.save()