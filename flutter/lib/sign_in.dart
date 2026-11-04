import 'package:flutter/material.dart';

/// A sign-in form: fields tagged with Semantics identifiers (what `id:` selects), a validation
/// error, a password field, and a loading veil over the form while it "signs in".
class SignIn extends StatefulWidget {
  const SignIn({super.key});

  @override
  State<SignIn> createState() => _SignInState();
}

class _SignInState extends State<SignIn> {
  final email = TextEditingController();
  final password = TextEditingController();
  bool remember = false;
  bool loading = false;
  String? error;

  Future<void> submit() async {
    if (email.text.isEmpty || password.text.isEmpty) {
      setState(() => error = 'Enter your email and password');
      return;
    }
    FocusScope.of(context).unfocus();
    setState(() {
      error = null;
      loading = true;
    });
    await Future<void>.delayed(const Duration(milliseconds: 1200));
    if (!mounted) return;
    setState(() => loading = false);
    Navigator.of(context).pushReplacement(
      MaterialPageRoute(
        builder: (_) => Welcome(email: email.text, remember: remember),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        Scaffold(
          appBar: AppBar(title: const Text('Sign in')),
          body: ListView(
            padding: const EdgeInsets.all(24),
            children: [
              Semantics(
                identifier: 'email',
                child: TextField(
                  controller: email,
                  keyboardType: TextInputType.emailAddress,
                  textInputAction: TextInputAction.next,
                  decoration: const InputDecoration(labelText: 'Email'),
                ),
              ),
              const SizedBox(height: 16),
              Semantics(
                identifier: 'password',
                child: TextField(
                  controller: password,
                  obscureText: true,
                  decoration: const InputDecoration(labelText: 'Password'),
                  onSubmitted: (_) => submit(),
                ),
              ),
              CheckboxListTile(
                contentPadding: EdgeInsets.zero,
                title: const Text('Remember me'),
                value: remember,
                onChanged: (v) => setState(() => remember = v ?? false),
              ),
              if (error != null)
                Text(
                  error!,
                  style: TextStyle(color: Theme.of(context).colorScheme.error),
                ),
              const SizedBox(height: 16),
              Semantics(
                identifier: 'submit',
                child: FilledButton(
                  onPressed: submit,
                  child: const Text('Sign in'),
                ),
              ),
            ],
          ),
        ),
        if (loading) ...[
          const ModalBarrier(dismissible: false, color: Colors.black38),
          const Center(child: CircularProgressIndicator()),
        ],
      ],
    );
  }
}

class Welcome extends StatelessWidget {
  const Welcome({super.key, required this.email, required this.remember});

  final String email;
  final bool remember;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Welcome')),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Signed in as $email'),
            Text(remember ? 'Remembered on this device' : 'Not remembered'),
            const SizedBox(height: 16),
            OutlinedButton(
              onPressed: () => Navigator.of(context).pushReplacement(
                MaterialPageRoute(builder: (_) => const SignIn()),
              ),
              child: const Text('Sign out'),
            ),
          ],
        ),
      ),
    );
  }
}
