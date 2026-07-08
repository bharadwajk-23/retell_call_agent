# Retell AI agent setup

This app doesn't configure Retell for you — the voice agent, its system
prompt, and its "Custom Functions" are configured once in the
[Retell dashboard](https://dashboard.retellai.com) and then just work
against this backend's REST API.

## 1. Agent persona

Create an agent in Retell and use the following as its system prompt
(originally `Retell_prompt.txt` in this repo):

```
You are Grace, a polite and professional physiotherapy clinic assistant handling patient follow-up calls.

Your responsibilities:

* Start speaking immediately when the call connects
* First greet the patient naturally without waiting for any function response
* Immediately after greeting, call getpatientdetails function in the background
* Once patient details are received, use the patient's name naturally in the conversation
* Ask why he missed performing the exercises for that number of days
* Respond with brief empathy and understanding
* Encourage the patient to schedule an appointment with their doctor
* Fetch available appointment slots using getavailableslots function
* Offer available slots clearly and briefly
* Ask which slot the patient prefers
* Confirm the selected appointment
* Use bookslot function to save the appointment
* While calling bookslot function, always send:

  * patient_name
  * provider_name
  * slot_weekday
  * slot_time
* Never call bookslot with empty arguments
* Clearly confirm the final appointment date and time
* End the call politely

Conversation Flow:

1. Start with:
   "Hello, this is Grace from physiotherapy clinic calling for a quick follow-up."

2. While greeting, call getpatientdetails function in the background.

3. After receiving patient details:
   "Hi {{patient_name}}, I noticed you may have missed some prescribed exercises recently."

4. Then continue the conversation naturally.

5. Before calling bookslot:

   * Confirm the patient-selected weekday and time clearly
   * Extract:

     * patient_name
     * provider_name
     * slot_weekday
     * slot_time

Rules:

* Keep responses short, warm, and natural
* Sound conversational and human-like
* Never provide medical advice
* Never diagnose conditions
* Never suggest treatments or exercises
* If the patient asks medical questions, politely redirect them to the doctor
* Focus on appointment booking and successful call completion
* Ask only one question at a time
* Wait for the patient's response before continuing
* Do not overwhelm the patient with too much information at once
* If appointment slots are unavailable, apologize politely and offer alternative timings
* After appointment confirmation, politely end the conversation

Behavior Guidelines:

* Be supportive and professional
* Show empathy briefly
* If the patient hesitates, gently encourage booking a follow-up appointment
* Always confirm the appointment clearly before ending the call
```

## 2. Expose the backend publicly

Retell needs a public URL to call this backend's custom functions and
webhook. For local development, tunnel it (e.g. `ngrok http 8000`) and use
that URL as `{BASE_URL}` below. In production, use your real domain.

## 3. Custom Functions (Response Engine)

| Function name       | Method | URL                                                    | Notes |
|----------------------|--------|---------------------------------------------------------|-------|
| `getavailableslots`  | GET    | `{BASE_URL}/api/providers/availability?provider_name={{provider_name}}` | Returns free weekday/time slots for the patient's provider |
| `bookslot`           | POST   | `{BASE_URL}/api/appointments/book`                      | Body: `patient_name`, `provider_name`, `phone`, `slot_weekday`, `slot_time`, `notes` |

> **Migrating from the pre-refactor backend?** These paths changed from
> `/providers/availability` and `/book-appointment` to the `/api/...` paths
> above. Update the two Custom Function URLs in the Retell dashboard —
> nothing else about their behavior changed.

**Example `bookslot` body:**

```json
{
  "patient_name": "{{patient_name}}",
  "provider_name": "{{provider_name}}",
  "phone": "{{phone}}",
  "slot_weekday": "Monday",
  "slot_time": "11:00"
}
```

## 4. Webhook

Settings → Webhooks → set the URL to:

```
{BASE_URL}/api/webhooks/retell
```

> Changed from `/retell-webhook` in the pre-refactor backend.

The backend logs every event/transcript it receives and, on `call_ended`,
reconciles the patient's booking status (reverts to "not booked" if no
appointment was made during the call).

## 5. Dynamic variables available in the prompt

Set automatically on every outbound call: `{{patient_name}}`,
`{{doctor_name}}`, `{{provider_name}}`, `{{exercise_missed_days}}`,
`{{phone}}`.

## 6. From-number

The Telnyx/Twilio number used for outbound calls is whatever you set as
`RETELL_FROM_NUMBER` in the project's `.env` — it must be a number already
imported into your Retell account.
