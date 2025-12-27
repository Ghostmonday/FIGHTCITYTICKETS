# Prettier Setup Guide

## ✅ Prettier is Safe to Apply

Prettier has been configured for this project. It will format:
- **TypeScript/TSX files** (`.ts`, `.tsx`)
- **JavaScript files** (`.js`, `.jsx`)
- **JSON files** (`.json`)
- **CSS files** (`.css`)
- **Markdown files** (`.md`)

## What's Excluded

The following are excluded from formatting (see `.prettierignore`):
- `node_modules/`
- `.next/` (Next.js build output)
- `public/` (static assets)
- Lock files (`package-lock.json`, etc.)

## Safe Application Steps

### 1. Install Prettier (if not already installed)
```bash
cd frontend
npm install
```

### 2. Check What Would Change (Recommended First Step)
```bash
npm run format:check
```

This will show you all files that would be reformatted **without making changes**.

### 3. Review the Changes
Review the output to see which files would be affected.

### 4. Apply Prettier Formatting
Once you're ready, apply formatting:
```bash
npm run format
```

Or format specific files:
```bash
npx prettier --write "app/**/*.tsx"
```

## Configuration

Prettier is configured in `.prettierrc.json`:
- **Semicolons**: Enabled
- **Trailing commas**: ES5 style
- **Quotes**: Double quotes
- **Print width**: 80 characters
- **Tab width**: 2 spaces
- **Line endings**: LF (Unix style)

## Integration with ESLint

If you want to integrate Prettier with ESLint (recommended), install:
```bash
npm install --save-dev eslint-config-prettier
```

Then update `.eslintrc.json` to extend Prettier config.

## Pre-commit Hook (Optional)

To automatically format on commit, install `husky` and `lint-staged`:
```bash
npm install --save-dev husky lint-staged
```

## Safety Notes

✅ **Safe because:**
- Prettier only changes formatting (whitespace, quotes, etc.)
- It doesn't change code logic
- Configuration is version-controlled
- You can review changes before applying

⚠️ **Before applying:**
1. Commit your current work
2. Run `format:check` first to see changes
3. Review the diff if applying to many files
4. Test your application after formatting

## Rollback

If you need to rollback formatting changes:
```bash
git checkout -- frontend/
```

Or revert specific files:
```bash
git checkout -- frontend/app/terms/page.tsx
```

