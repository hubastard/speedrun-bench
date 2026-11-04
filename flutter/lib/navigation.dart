import 'package:flutter/material.dart';

/// App-level navigation: a bottom navigation bar whose tabs keep their state, a drawer, and a
/// nested screen left with the system back (Android) or the app bar's back button.
class Navigation extends StatefulWidget {
  const Navigation({super.key});

  @override
  State<Navigation> createState() => _NavigationState();
}

class _NavigationState extends State<Navigation> {
  int tab = 0;
  String drawerChoice = 'No drawer choice';

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(['Home tab', 'Search tab', 'Profile tab'][tab]),
      ),
      drawer: Drawer(
        child: ListView(
          children: [
            const DrawerHeader(child: Text('Menu')),
            for (final item in ['Settings', 'Help'])
              ListTile(
                title: Text(item),
                onTap: () {
                  Navigator.pop(context);
                  setState(() => drawerChoice = 'Opened $item');
                },
              ),
          ],
        ),
      ),
      body: IndexedStack(
        index: tab,
        children: [
          Center(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(drawerChoice),
                const SizedBox(height: 16),
                FilledButton(
                  onPressed: () => Navigator.of(context)
                      .push(MaterialPageRoute(builder: (_) => const Nested())),
                  child: const Text('Open nested screen'),
                ),
              ],
            ),
          ),
          const Padding(
            padding: EdgeInsets.all(16),
            child: TextField(decoration: InputDecoration(labelText: 'Search')),
          ),
          const Center(child: Text('Ada Lovelace')),
        ],
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: tab,
        onDestinationSelected: (i) => setState(() => tab = i),
        destinations: const [
          NavigationDestination(icon: Icon(Icons.home), label: 'Home'),
          NavigationDestination(icon: Icon(Icons.search), label: 'Search'),
          NavigationDestination(icon: Icon(Icons.person), label: 'Profile'),
        ],
      ),
    );
  }
}

class Nested extends StatelessWidget {
  const Nested({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Nested screen')),
      body: const Center(child: Text('Deep in the stack')),
    );
  }
}
