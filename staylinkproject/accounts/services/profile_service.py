from accounts.models import OwnerProfile, BrokerProfile


def create_owner_profile(user, serializer):
    if user.role != 'owner':
        raise Exception("Only owners allowed")

    if OwnerProfile.objects.filter(user=user).exists():
        raise Exception("Profile already exists")

    profile = serializer.save(user=user)

    user.profile_completed = True
    user.save()

    return profile


def create_broker_profile(user, serializer):
    if user.role != 'broker':
        raise Exception("Only brokers allowed")

    if BrokerProfile.objects.filter(user=user).exists():
        raise Exception("Profile already exists")

    profile = serializer.save(user=user)

    user.profile_completed = True
    user.save()

    return profile


def get_owner_profile(user):
    try:
        return OwnerProfile.objects.get(user=user)
    except OwnerProfile.DoesNotExist:
        raise Exception("Owner profile not found")


def update_owner_profile(user, serializer):
    try:
        profile = OwnerProfile.objects.get(user=user)
    except OwnerProfile.DoesNotExist:
        raise Exception("Profile does not exist")

    serializer.save(user=user)  # update existing instance
    return serializer.instance