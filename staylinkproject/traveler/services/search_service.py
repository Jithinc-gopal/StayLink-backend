from django.db.models import Q

from owner.models import Property


class PropertySearchService:

    @staticmethod
    def search_properties(filters):

        queryset = Property.objects.filter(
            status='active',
            is_available=True
        )

        # =========================
        # LOCATION SEARCH
        # =========================

        location = filters.get('location')

        if location:

            queryset = queryset.filter(

                Q(city__icontains=location) |

                Q(state__icontains=location) |

                Q(address__icontains=location)
            )

        # =========================
        # PROPERTY TYPE
        # =========================

        property_type = filters.get('property_type')

        if property_type:

            queryset = queryset.filter(
                property_type=property_type
            )

        # =========================
        # GUEST COUNT
        # =========================

        guests = filters.get('guests')

        if guests:

            queryset = queryset.filter(
                max_guest__gte=guests
            )

        # =========================
        # MIN PRICE
        # =========================

        min_price = filters.get('min_price')

        if min_price:

            queryset = queryset.filter(
                price__gte=min_price
            )

        # =========================
        # MAX PRICE
        # =========================

        max_price = filters.get('max_price')

        if max_price:

            queryset = queryset.filter(
                price__lte=max_price
            )

        return queryset.order_by('-created_at')