import 'package:flutter/material.dart';

/// A form longer than the screen: fields the keyboard covers, a multiline field, a number
/// field, and a Save button at the end that shows what each field holds. A tap outside the
/// fields closes the keyboard, as many apps do: a multiline field or a number pad has no key
/// that does on iOS.
class KeyboardLab extends StatefulWidget {
  const KeyboardLab({super.key});

  @override
  State<KeyboardLab> createState() => _KeyboardLabState();
}

class _KeyboardLabState extends State<KeyboardLab> {
  final fields = [for (var i = 0; i < 8; i++) TextEditingController()];
  final notes = TextEditingController();
  final amount = TextEditingController();
  String saved = '';

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () => FocusManager.instance.primaryFocus?.unfocus(),
      child: Scaffold(
        appBar: AppBar(title: const Text('Keyboard')),
        body: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            for (var i = 0; i < fields.length; i++)
              Padding(
                padding: const EdgeInsets.only(bottom: 12),
                child: TextField(
                  controller: fields[i],
                  decoration: InputDecoration(labelText: 'Field ${i + 1}'),
                ),
              ),
            TextField(
              controller: notes,
              maxLines: 3,
              decoration: const InputDecoration(labelText: 'Notes'),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: amount,
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(labelText: 'Amount'),
            ),
            const SizedBox(height: 16),
            FilledButton(
              onPressed: () => setState(
                () => saved =
                    'Saved: ${fields.first.text} / ${fields.last.text} / ${notes.text.replaceAll('\n', ' ')} / ${amount.text}',
              ),
              child: const Text('Save'),
            ),
            if (saved.isNotEmpty)
              Padding(
                padding: const EdgeInsets.only(top: 12),
                child: Text(saved),
              ),
          ],
        ),
      ),
    );
  }
}
