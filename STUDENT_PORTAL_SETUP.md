# Student portal setup

The first portal slice is student-only. Agent and university accounts are intentionally deferred.

## What is included

- Student registration with email, phone and password.
- Token login using the existing Django user system.
- Profile completion for Nepali identity, academic, grading, language and study-goal details.
- Admin-controlled document checklist.
- Direct browser uploads to private Storj using short-lived presigned PUT URLs.
- Presigned GET URLs for a student’s own documents.
- Admin-managed applications, stages and recommendation requests.
- AI course-guidance requests through the OpenAI Responses API when configured.

## Render environment variables

Set these on the backend service:

```text
USE_STORJ=true
STORJ_ACCESS_KEY=...
STORJ_SECRET_KEY=...
STORJ_BUCKET=...
STORJ_ENDPOINT=https://gateway.storjshare.io

# Optional. Without this, AI requests remain queued for admin/admission review.
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-5
```

Run the normal deploy migration before opening the portal:

```bash
python manage.py migrate
```

## Storj bucket CORS

Because the browser uploads directly to Storj, the bucket must allow the deployed frontend origin. Apply the example policy with the Storj S3-compatible endpoint, replacing the origins with the real production and local frontend URLs:

```bash
aws --endpoint-url https://gateway.storjshare.io s3api put-bucket-cors \
  --bucket YOUR_BUCKET \
  --cors-configuration file://storj-cors.example.json
```

The backend still authorizes every upload and download. The CORS policy does not make the bucket public.

## Recommendation behavior

AI guidance is a first-pass educational shortlist restricted to the published course catalog. It is not an admission, scholarship or visa decision. Admission Head requests are saved as admin work items and can be completed from Django admin with course recommendations and rationale.

The AI prompt excludes passport, citizenship, address and emergency-contact data. Google and GitHub login require OAuth client credentials and callback verification, so they remain a later authentication phase rather than being enabled with unsafe defaults.
