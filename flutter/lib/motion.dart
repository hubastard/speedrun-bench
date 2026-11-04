import 'package:flutter/material.dart';

/// What keeps a Flutter screen drawing: a spinner that never stops (a settle must not wait for
/// it), a result that comes in late, items that animate into a list, and a busy Dart isolate
/// right after a tap (the UI thread blocked before the screen changes).
class Motion extends StatefulWidget {
  const Motion({super.key});

  @override
  State<Motion> createState() => _MotionState();
}

class _MotionState extends State<Motion> {
  final list = GlobalKey<AnimatedListState>();
  final items = <String>[];
  String status = 'Idle';
  int taps = 0;

  Future<void> load() async {
    setState(() => status = 'Loading');
    await Future<void>.delayed(const Duration(milliseconds: 1500));
    if (mounted) setState(() => status = 'Loaded 3 items');
  }

  void add() {
    items.insert(0, 'Item ${items.length + 1}');
    list.currentState!.insertItem(
      0,
      duration: const Duration(milliseconds: 400),
    );
  }

  void busy() {
    // Work on the UI thread before the screen changes, as an app parsing a big reply does.
    final end = DateTime.now().add(const Duration(milliseconds: 700));
    while (DateTime.now().isBefore(end)) {}
    setState(() => status = 'Crunched');
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Motion')),
      body: Column(
        children: [
          const Padding(
            padding: EdgeInsets.all(16),
            child: LinearProgressIndicator(),
          ),
          Text('Status: $status'),
          Wrap(
            spacing: 8,
            children: [
              FilledButton(onPressed: load, child: const Text('Load')),
              FilledButton(
                onPressed: () => setState(() => taps++),
                child: const Text('Tap while spinning'),
              ),
              FilledButton(onPressed: add, child: const Text('Add item')),
              FilledButton(onPressed: busy, child: const Text('Crunch')),
            ],
          ),
          Text('Taps: $taps'),
          AnimatedSwitcher(
            duration: const Duration(milliseconds: 500),
            child: Text(
              status == 'Loaded 3 items' ? 'Ready' : 'Not ready',
              key: ValueKey(status == 'Loaded 3 items'),
            ),
          ),
          Expanded(
            child: AnimatedList(
              key: list,
              itemBuilder: (context, i, animation) => SizeTransition(
                sizeFactor: animation,
                child: ListTile(title: Text(items[i])),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
