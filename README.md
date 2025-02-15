# ctfd-yandex-captcha

Plugin that adds [Yandex SmartCaptcha](https://yandex.cloud/en/docs/smartcaptcha/quickstart) to the registration form of CTFd.

![](./screenshots/example.png)

## How to use?

1. Create and configure captcha in Yandex Cloud console (you can use [this guide](https://yandex.cloud/en/docs/smartcaptcha/quickstart#creat-captcha) to do so).
2. Add captcha keys to `YSC_CLIENT_KEY` and `YSC_SERVER_KEY` environment variables of `ctfd` container.
3. Copy this repository to CTFd plugins directory, which is located at `CTFd/plugins`.

That's all!

> [!WARNING]
>
> If you don't specify environment variables for `ctfd` container, captcha will not be present, and message
> `Captcha is disabled because variable {ENV_VAR_KEY} is not present in environment` will be displayed in logs.

## Contributing

If you have any suggestions for improvements or fixes to this plugin, please feel free to create a pull request. You can also create an issue to discuss your suggestions or propose new features.
