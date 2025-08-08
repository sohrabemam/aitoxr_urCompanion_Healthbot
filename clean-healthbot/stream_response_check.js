const params = new URLSearchParams({
  user_id: "fbcb388a-c847-4025-845e-c5b37d185f3b",
  is_paid: true
});
const response = await fetch(`/conversations/?${params.toString()}`, {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
  "title": "My Conversation Title",
  "first_message": {
    "content": "Hello, this is the first message"
  }
}
),
});

const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
  const { value, done } = await reader.read();
  if (done) break;

  const chunk = decoder.decode(value);
  // Handle the chunk (e.g., append to UI)
  console.log(chunk);
}