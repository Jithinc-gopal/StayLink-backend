from accounts.models import (
    OwnerProfile,
    BrokerProfile
)

from accounts.utils.email_service import (
    send_owner_profile_pending_email,
    send_admin_owner_notification,
    send_broker_profile_pending_email,
    send_admin_broker_notification
)



def create_owner_profile(user, serializer):

    if user.role != 'owner':
        raise Exception("Only owners allowed")

    if OwnerProfile.objects.filter(user=user).exists():
        raise Exception("Profile already exists")

    profile = serializer.save(user=user)

    user.profile_completed = True
    user.save()

    # EMAIL TO OWNER
    try:
        send_owner_profile_pending_email(user)

    except Exception as e:
        print(f"Owner email error: {e}")

    # EMAIL TO ADMIN
    try:
        send_admin_owner_notification(user)

    except Exception as e:
        print(f"Admin owner email error: {e}")

    return profile




def create_broker_profile(user, serializer):

    if user.role != 'broker':
        raise Exception("Only brokers allowed")

    if BrokerProfile.objects.filter(user=user).exists():
        raise Exception("Profile already exists")

    profile = serializer.save(user=user)

    user.profile_completed = True
    user.save()

    # EMAIL TO BROKER
    try:
        send_broker_profile_pending_email(user)

    except Exception as e:
        print(f"Broker email error: {e}")

    # EMAIL TO ADMIN
    try:
        send_admin_broker_notification(user)

    except Exception as e:
        print(f"Admin broker email error: {e}")

    return profile



def get_owner_profile(user):

    try:
        return OwnerProfile.objects.get(user=user)

    except OwnerProfile.DoesNotExist:
        raise Exception("Owner profile not found")



def update_owner_profile(user, serializer):

    try:
        OwnerProfile.objects.get(user=user)

    except OwnerProfile.DoesNotExist:
        raise Exception("Profile does not exist")

    updated_profile = serializer.save(user=user)

    return updated_profile



def get_broker_profile(user):

    try:
        return BrokerProfile.objects.get(user=user)

    except BrokerProfile.DoesNotExist:
        raise Exception("Broker profile not found")
    
    
    
def update_broker_profile(user, serializer):

    try:
        BrokerProfile.objects.get(user=user)

    except BrokerProfile.DoesNotExist:
        raise Exception("Profile does not exist")

    updated_profile = serializer.save(user=user)

    return updated_profile    