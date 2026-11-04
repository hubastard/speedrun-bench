import 'package:flutter/material.dart';

/// Material controls (switch, checkbox, slider, segmented button, icon buttons known by their
/// tooltip), a long press, and a target with both a tap and a double tap: Flutter holds its
/// single tap until the double tap's time is out (300 ms).
class Controls extends StatefulWidget {
  const Controls({super.key});

  @override
  State<Controls> createState() => _ControlsState();
}

class _ControlsState extends State<Controls> {
  bool wifi = false;
  bool terms = false;
  double volume = 20;
  String range = 'Week';
  int count = 0;
  String gesture = 'No gesture';

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Controls')),
      body: ListView(
        padding: const EdgeInsets.symmetric(vertical: 8),
        children: [
          SwitchListTile(
            title: const Text('Wi-Fi'),
            value: wifi,
            onChanged: (v) => setState(() => wifi = v),
          ),
          CheckboxListTile(
            title: const Text('Accept terms'),
            value: terms,
            onChanged: (v) => setState(() => terms = v ?? false),
          ),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: Text(
              'Wi-Fi ${wifi ? 'on' : 'off'}, terms ${terms ? 'accepted' : 'not accepted'}',
            ),
          ),
          Slider(
            value: volume,
            max: 100,
            divisions: 10,
            label: '${volume.round()}',
            onChanged: (v) => setState(() => volume = v),
          ),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: Text('Volume ${volume.round()}'),
          ),
          Padding(
            padding: const EdgeInsets.all(16),
            child: SegmentedButton<String>(
              segments: const [
                ButtonSegment(value: 'Day', label: Text('Day')),
                ButtonSegment(value: 'Week', label: Text('Week')),
                ButtonSegment(value: 'Month', label: Text('Month')),
              ],
              selected: {range},
              onSelectionChanged: (s) => setState(() => range = s.first),
            ),
          ),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: Text('Range: $range'),
          ),
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              IconButton(
                tooltip: 'Decrement',
                icon: const Icon(Icons.remove),
                onPressed: () => setState(() => count--),
              ),
              Text('Count: $count'),
              IconButton(
                tooltip: 'Increment',
                icon: const Icon(Icons.add),
                onPressed: () => setState(() => count++),
              ),
            ],
          ),
          Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                Expanded(
                  child: Card(
                    child: InkWell(
                      onLongPress: () => setState(() => gesture = 'Held'),
                      child: const Padding(
                        padding: EdgeInsets.all(24),
                        child: Center(child: Text('Hold me')),
                      ),
                    ),
                  ),
                ),
                Expanded(
                  child: Card(
                    child: GestureDetector(
                      behavior: HitTestBehavior.opaque,
                      onTap: () => setState(() => gesture = 'Tapped once'),
                      onDoubleTap: () =>
                          setState(() => gesture = 'Tapped twice'),
                      child: const Padding(
                        padding: EdgeInsets.all(24),
                        child: Center(child: Text('Tap or double tap')),
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: Text('Gesture: $gesture'),
          ),
        ],
      ),
    );
  }
}
