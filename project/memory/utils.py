from django.db.models import Q


def get_user_social_info(user) -> dict:
    """
    Returns social info of the passed user or {"user_error": "..."} if
    user does not have a related social_account with Google or Vk provider.
    """
    if not user.is_authenticated:
        return {
            "user_error": "The passed user is not User object."
        }

    user_related_social_account = user.socialaccount_set.filter(
        Q(provider="google") | Q(provider="vk")).first()

    if user_related_social_account is None:
        return {
            "user_error":
                "This account is not associated with a Google or VK account, "
                "please log in again using these services."
        }

    if user_related_social_account.provider in ["google", "vk"]:
        # Use different methods for Google and Vk providers to get user_name
        # Because they provide different data
        user_name = {
            "google": lambda user_data: user_data.get("name", "google_user_name"),
            "vk": lambda user_data: f"{user_data.get('first_name', 'vk_first_name')} {user_data.get('last_name', 'vk_last_name')}",
        }[user_related_social_account.provider](
            user_related_social_account.extra_data)
    else:
        return {
            "user_error": "Unresolved provider."
        }

    return {
        "user_name": user_name,
        "user_picture": user_related_social_account.get_avatar_url(),
    }
