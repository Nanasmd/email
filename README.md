
```markdown
# 📧 Email Utility

A minimal, secure, and developer-friendly CLI + API for sending emails via SMTP — without the bloat.

---

## 🚀 Features

- ✅ Send plaintext and HTML emails
- ✅ CLI and programmatic usage
- ✅ Attachment support
- ✅ ENV-based configuration (no hardcoded secrets)
- ⚙️ Ready for containerization and CI integration

---

## 🧰 Requirements

- Node.js >= 14
- A valid SMTP provider (e.g. Gmail, SendGrid, Mailgun)
- Environment variables:



SMTP\_HOST=
SMTP\_PORT=
SMTP\_USER=
SMTP\_PASS=

````

---

## 🛠️ Installation

```bash
git clone https://github.com/Nanasmd/email.git
cd email
npm install
````

---

## 📦 Usage

### CLI Example

```bash
node bin/email.js \
  --to="recipient@example.com" \
  --subject="Hello" \
  --body="This is a test email." \
  --html
```

### Programmatic Example

```js
import { sendEmail } from './src/index.js';

await sendEmail({
  to: 'you@example.com',
  subject: 'Test Email',
  text: 'Hello world',
  html: '<strong>Hello world</strong>',
});
```

---

## 🔧 Configuration

| ENV Variable | Description            | Example              |
| ------------ | ---------------------- | -------------------- |
| `SMTP_HOST`  | SMTP server host       | `smtp.gmail.com`     |
| `SMTP_PORT`  | SMTP port              | `587`                |
| `SMTP_USER`  | SMTP login username    | `you@example.com`    |
| `SMTP_PASS`  | SMTP password or token | `your_smtp_password` |

Use a `.env` file or set these in your deployment environment.

---

## 🧪 Testing

To run tests:

```bash
npm test
```

You can use a sandbox SMTP service like [Mailtrap](https://mailtrap.io) for safe testing.

---

## 🛡️ Security Notes

* TLS enforced if supported by the SMTP server
* No credentials stored or logged
* Input sanitized to prevent header injection
* Designed to be run inside secure containers or CI pipelines

---

## 🤝 Contributing

1. Fork the project
2. Create your feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m 'Add new feature'`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a pull request

---

## 📄 License

MIT © [Nassrine Samadi](https://github.com/Nanasmd)

---

## ❓ Support

For bugs, open an [issue](https://github.com/Nanasmd/email/issues).
For feature requests or questions, contact me directly.

```

Let me know if you want:

- GitHub Actions CI config
- Dockerfile
- Email templating integration (e.g. EJS, MJML)
- Support for OAuth or API-based email services

Ready to scale this into a deployable microservice or stay lean and local?
```
