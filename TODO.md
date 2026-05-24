# npm publishing setup — remaining manual steps

## 1. Claim the package name (one-time bootstrap)

From the repo root:

```bash
npm login          # opens browser for npmjs.com auth
npm whoami         # confirm login
npm publish --access public
```

This creates `codeforerunner` on npmjs.com. Only needed once.

## 2. Configure trusted publisher on npmjs.com

After the package exists:

1. npmjs.com → your profile → **Packages** → `codeforerunner`
2. **Settings** → **Trusted publishing** → **Add a trusted publisher**
3. Select **GitHub Actions**, fill in:
   - Repository owner: `derek-palmer`
   - Repository name: `codeforerunner`
   - Workflow filename: `npm-publish.yml`
   - Environment name: `npm`
4. Save

## 3. Done — all future releases are fully automated

Every `git tag vX.Y.Z && git push origin vX.Y.Z` triggers both:
- **PyPI** publish (already working, OIDC tokenless via `pypi-publish.yml`)
- **npm** publish (tokenless after step 2, via `npm-publish.yml`)

No secrets to manage. No tokens to rotate.
