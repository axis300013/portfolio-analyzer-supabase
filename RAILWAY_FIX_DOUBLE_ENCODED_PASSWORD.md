# Fix DATABASE_URL with Special Character Password

**The Problem:**
- Password contains `#` which breaks URL parsing
- URL encoding `%23` also doesn't work in SQLAlchemy

**The Solution:**

In Railway Variables Raw editor, use this exact format:

```
postgresql://postgres:Clobufclobuf01%2523@db.hrlzrirsvifxsnccxvsa.supabase.co:5432/postgres
```

**Key difference:** Use `%2523` instead of `%23`
- `%25` = encoded `%`
- `%23` = encoded `#`
- Together: `%2523` = double-encoded `#`

---

## Steps:

1. Go to Railway Dashboard → Your service → Variables tab
2. Click "Raw" editor
3. Find the DATABASE_URL line
4. Replace with:
   ```
   DATABASE_URL=postgresql://postgres:Clobufclobuf01%2523@db.hrlzrirsvifxsnccxvsa.supabase.co:5432/postgres
   ```
5. Click Save
6. Click "Trigger Deploy"
7. Wait 3-5 minutes

---

**Why this works:**
- SQLAlchemy decodes `%2523` → `%23` → SQLAlchemy decodes again → `#`
- Double encoding preserves the actual `#` character in the password

Let me know when deployed!
