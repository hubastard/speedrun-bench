import 'package:flutter/material.dart';

import 'controls.dart';
import 'feed.dart';
import 'keyboard.dart';
import 'motion.dart';
import 'navigation.dart';
import 'pager.dart';
import 'popups.dart';
import 'sign_in.dart';

void main() => runApp(const FlutterBench());

/// Flutter Bench: the Flutter patterns UI test tools trip on, one screen each. Speedrun's
/// Flutter flows (flows/) run against it.
class FlutterBench extends StatelessWidget {
  const FlutterBench({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Flutter Bench',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(colorSchemeSeed: Colors.indigo),
      home: const Home(),
    );
  }
}

class Home extends StatelessWidget {
  const Home({super.key});

  static final labs = <String, Widget Function()>{
    'Sign in': () => const SignIn(),
    'Feed': () => const Feed(),
    'Popups': () => const Popups(),
    'Controls': () => const Controls(),
    'Pager': () => const Pager(),
    'Keyboard': () => const KeyboardLab(),
    'Motion': () => const Motion(),
    'Navigation': () => const Navigation(),
  };

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Flutter Bench')),
      body: ListView(
        children: [
          for (final MapEntry(key: name, value: page) in labs.entries)
            ListTile(
              title: Text(name),
              trailing: const Icon(Icons.chevron_right),
              onTap: () =>
                  Navigator.of(context)
                      .push(MaterialPageRoute(builder: (_) => page())),
            ),
        ],
      ),
    );
  }
}
