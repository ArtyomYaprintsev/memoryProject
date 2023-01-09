import json

from django.test import TestCase
from django.contrib.auth.models import User

from .forms import MemoryForm

user = {
    "username": "test_user",
    "email": "test_user@unknown.com",
    "password": "test_user_password",
}

valid_location = "[55.7558,37.6173]"
additional_valid_location = "[40.7128,74.0060]"
invalid_location = "Moscow"


class CreateMemoryTemplateTest(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username=user["username"],
            email=user["email"],
            password=user["password"]
        )
        self.client.login(username=user["username"], password=user["password"])
        self.response = self.client.get("/memory/create/")

    def test_template(self):
        return self.assertTemplateUsed(self.response, "create_memory.html")

    def test_has_form(self):
        form = self.response.context["form"]
        return self.assertIsInstance(form, MemoryForm)

    def test_html_form(self):
        self.assertContains(self.response, "<form")

        self.assertContains(self.response, 'name="user"', 1)
        self.assertContains(self.response, 'name="location"', 1)
        self.assertContains(self.response, 'name="name"', 1)
        self.assertContains(self.response, 'name="description"', 1)

        self.assertContains(self.response, 'type="hidden"', 3)
        self.assertContains(self.response, 'type="text"', 1)
        self.assertContains(self.response, "<textarea", 1)

    def test_csrf(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')


class CreateMemoryLogicTest(TestCase):
    @staticmethod
    def util_parse_messages(response) -> list:
        messages = list(map(
            lambda m: (m.tags, json.loads(m.message)),
            response.context["messages"]
        ))
        return messages

    def setUp(self) -> None:
        self.url = "/memory/create/"

        self.user = User.objects.create_user(
            username=user["username"],
            email=user["email"],
            password=user["password"]
        )

        self.client.login(username=user["username"], password=user["password"])

    def test_create_memory_without_required_fields(self):
        empty_memory_info = {}

        response = self.client.post(
            self.url, empty_memory_info
        )

        messages = self.util_parse_messages(response)

        self.assertEqual(len(messages), 1)

        tag, message_info = messages[0]

        self.assertEqual(tag, "error")

        required_fields = ["user", "name", "location"]
        message_error_code = "required"

        for required_field in required_fields:
            self.assertIn(required_field, message_info)
            self.assertEqual(
                message_error_code,
                message_info[required_field][0]["code"]
            )

    def test_create_memory_with_invalid_fields(self):
        invalid_memory_info = {
            "user": "abc",
            "location": invalid_location,
            "name": "*" * 101,
            "description": "*" * 251,
        }

        response = self.client.post(
            self.url, invalid_memory_info
        )

        messages = self.util_parse_messages(response)

        self.assertEqual(len(messages), 1)

        tag, message_info = messages[0]

        self.assertEqual(tag, "error")

        invalid_fields = [
            {
                "field_name": "user",
                "expected_error_code": "invalid_choice"
            },
            {
                "field_name": "name",
                "expected_error_code": "max_length"
            },
            {
                "field_name": "description",
                "expected_error_code": "max_length"
            },
            {
                "field_name": "location",
                "expected_error_code": "invalid"
            }
        ]

        for invalid_field in invalid_fields:
            self.assertIn(invalid_field["field_name"], message_info)
            self.assertEqual(
                invalid_field["expected_error_code"],
                message_info[invalid_field["field_name"]][0]["code"]
            )

    def test_create_memory_with_unique_fields(self):
        valid_memory_info = {
            "user": self.user.id,
            "name": "test-unique-memory-name",
            "description": "test-memory-description",
            "location": valid_location
        }

        self.user.memory_set.create(
            name=valid_memory_info["name"],
            description=valid_memory_info["description"],
            location=valid_memory_info["location"],
        )

        response = self.client.post(
            self.url, valid_memory_info
        )

        messages = self.util_parse_messages(response)

        self.assertEqual(len(messages), 1)

        tag, _ = messages[0]

        self.assertEqual(tag, "error")

        memories_with_same_name = self.user.memory_set \
            .filter(name=valid_memory_info["name"])

        self.assertEqual(len(memories_with_same_name), 1)

        memories_with_same_location = self.user.memory_set \
            .filter(location=valid_memory_info["location"])

        self.assertEqual(len(memories_with_same_location), 1)

    def test_create_memory_successfully(self):
        valid_memory_info = {
            "user": self.user.id,
            "name": "test-memory-name",
            "description": "test-memory-description",
            "location": valid_location
        }

        response = self.client.post(
            self.url, valid_memory_info
        )

        self.assertRedirects(
            response, "/memory/list/",
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True
        )

        memory = self.user.memory_set.filter(
            user=self.user,
            name=valid_memory_info["name"],
            location=valid_memory_info["location"]
        ).first()

        self.assertIsNotNone(memory)


class GetMemoryListTest(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username=user["username"],
            email=user["email"],
            password=user["password"]
        )

        self.client.login(
            username=user["username"],
            password=user["password"]
        )

        # Initialize list of memories
        self.memories = []
        for index, location in \
                enumerate([valid_location, additional_valid_location]):
            self.memories.append(
                self.user.memory_set.create(
                    name=f"test-list-memory-{index}",
                    description=f"test-list-memory-description-{index}",
                    location=location
                )
            )

        self.response = self.client.get("/memory/list/")

    def test_template(self):
        return self.assertTemplateUsed(self.response, "list_memory.html")

    def test_html_response(self):
        self.assertContains(self.response, "<table"),

        self.assertContains(self.response, "<tr", len(self.memories) + 1)

        for memory in self.memories:
            self.assertContains(
                self.response, f'<th scope="row">{memory.id}</th>', 1
            )


class EditMemoryLogicTest(TestCase):
    def setUp(self) -> None:
        self.url_format = "/memory/edit/{memory_id}/"

        self.user = User.objects.create_user(
            username=user["username"],
            email=user["email"],
            password=user["password"]
        )

        self.client.login(
            username=user["username"],
            password=user["password"]
        )

        self.initial_memory = self.user.memory_set.create(
            name="test-edit-memory-name",
            description="test-edit-memory-description",
            location=valid_location
        )

    def test_edit_unavailable_memory(self):
        response = self.client.get(
            self.url_format.format(memory_id=self.initial_memory.id + 1)
        )

        self.assertRedirects(
            response, "/memory/list/",
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True
        )

    def test_edit_memory_successfully(self):
        initial_memory_set_length = len(self.user.memory_set.all())

        _updated_memory_info = {
            "user": self.user.id,
            "name": f"{self.initial_memory.name}-changed",
            "description": f"{self.initial_memory.description}-changed",
            "location": additional_valid_location,
        }

        self.client.post(
            self.url_format.format(memory_id=self.initial_memory.id),
            _updated_memory_info
        )

        self.assertEqual(
            len(self.user.memory_set.all()),
            initial_memory_set_length
        )

        initial_memory_info = self.initial_memory.memory_info()
        updated_memory_info = self.user.memory_set \
            .get(id=self.initial_memory.id) \
            .memory_info()

        updated_fields = ["name", "description", "location"]
        for updated_field in updated_fields:
            self.assertEqual(
                _updated_memory_info[updated_field],
                updated_memory_info[updated_field]
            )
            self.assertNotEqual(
                updated_memory_info[updated_field],
                initial_memory_info[updated_field]
            )


class DeleteMemoryLogicTest(TestCase):
    def setUp(self) -> None:
        self.url_format = "/memory/delete/{memory_id}/"

        self.user = User.objects.create_user(
            username=user["username"],
            email=user["email"],
            password=user["password"]
        )

        self.initial_memory = self.user.memory_set.create(
            name="test-edit-memory-name",
            description="test-edit-memory-description",
            location=valid_location
        )

        self.client.login(
            username=user["username"],
            password=user["password"]
        )

    def test_delete_unavailable_memory(self):
        response = self.client.get(
            self.url_format.format(memory_id=self.initial_memory.id + 1)
        )

        self.assertRedirects(
            response, "/memory/list/",
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True
        )

    def test_delete_memory_successfully(self):
        initial_memory_set_length = len(self.user.memory_set.all())

        self.client.get(
            self.url_format.format(memory_id=self.initial_memory.id)
        )

        self.assertEqual(
            len(self.user.memory_set.all()) + 1,
            initial_memory_set_length
        )

        memory = self.user.memory_set.filter(
            name=self.initial_memory.name
        ).first()

        self.assertIsNone(memory)
