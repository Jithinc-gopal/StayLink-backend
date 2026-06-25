from django.db.models import Q
from owner.models import Property


class PropertySearchService:

    @staticmethod
    def search_properties(filters):

        queryset = (
            Property.objects
            .filter(
                status="active",
                is_available=True
            )
            .prefetch_related(
                "images",
                "property_amenities__amenity"
            )
        )

        location = filters.get("location")

        if location:
            queryset = queryset.filter(
                Q(city__icontains=location) |
                Q(state__icontains=location) |
                Q(address__icontains=location) |
                Q(title__icontains=location) |
                Q(description__icontains=location) |
                Q(nearby_facilities__icontains=location) |
                Q(property_amenities__amenity__name__icontains=location)
            )

        property_type = filters.get("property_type")

        if property_type:
            queryset = queryset.filter(
                property_type=property_type
            )

        guests = filters.get("guests")

        if guests:
            queryset = queryset.filter(
                max_guest__gte=int(guests)
            )

        max_price = filters.get("max_price")

        if max_price:
            queryset = queryset.filter(
                price__lte=float(max_price)
            )

        min_price = filters.get("min_price")

        if min_price:
            queryset = queryset.filter(
                price__gte=float(min_price)
            )

        furnished = filters.get("furnished")

        if furnished == "true":
            queryset = queryset.filter(
                is_furnished=True
            )

        ordering = filters.get("ordering")

        allowed_ordering = [
            "price",
            "-price",
            "created_at",
            "-created_at",
            "max_guest",
            "-max_guest",
        ]

        if ordering in allowed_ordering:
            queryset = queryset.order_by(ordering)
        else:
            queryset = queryset.order_by("-created_at")

        return queryset.distinct()