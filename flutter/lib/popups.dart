import 'package:flutter/material.dart';

/// What Flutter draws over a screen in its own overlay (one Android view, one iOS view): a
/// dialog, a modal bottom sheet with a long list, a snack bar with an action, a popup menu,
/// a dropdown menu.
class Popups extends StatefulWidget {
  const Popups({super.key});

  @override
  State<Popups> createState() => _PopupsState();
}

class _PopupsState extends State<Popups> {
  String result = 'Nothing yet';
  String fruit = 'Apple';

  void show(String text) => setState(() => result = text);

  Future<void> dialog() async {
    final delete = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete draft?'),
        content: const Text('The draft goes for good.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('Delete'),
          ),
        ],
      ),
    );
    show(delete == true ? 'Draft deleted' : 'Kept the draft');
  }

  Future<void> sheet() async {
    final picked = await showModalBottomSheet<String>(
      context: context,
      showDragHandle: true,
      isScrollControlled: true,
      builder: (context) => DraggableScrollableSheet(
        expand: false,
        initialChildSize: 0.5,
        maxChildSize: 0.9,
        builder: (context, controller) => ListView.builder(
          controller: controller,
          itemCount: 40,
          itemBuilder: (context, i) => ListTile(
            title: Text('Account ${i + 1}'),
            onTap: () => Navigator.pop(context, 'Account ${i + 1}'),
          ),
        ),
      ),
    );
    show(picked == null ? 'No account picked' : 'Picked $picked');
  }

  void snack() {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: const Text('Message archived'),
        action: SnackBarAction(
          label: 'Undo',
          onPressed: () => show('Message restored'),
        ),
      ),
    );
    show('Archived');
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Popups'),
        actions: [
          PopupMenuButton<String>(
            tooltip: 'More',
            onSelected: (v) => show('Chose $v'),
            itemBuilder: (context) => const [
              PopupMenuItem(value: 'Share', child: Text('Share')),
              PopupMenuItem(value: 'Rename', child: Text('Rename')),
            ],
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.all(24),
        children: [
          Text(result, style: Theme.of(context).textTheme.titleMedium),
          const SizedBox(height: 16),
          FilledButton(onPressed: dialog, child: const Text('Show dialog')),
          const SizedBox(height: 8),
          FilledButton(onPressed: sheet, child: const Text('Show sheet')),
          const SizedBox(height: 8),
          FilledButton(onPressed: snack, child: const Text('Archive message')),
          const SizedBox(height: 16),
          DropdownMenu<String>(
            label: const Text('Fruit'),
            initialSelection: fruit,
            onSelected: (v) => setState(() {
              fruit = v ?? fruit;
              result = 'Fruit: $fruit';
            }),
            dropdownMenuEntries: const [
              DropdownMenuEntry(value: 'Apple', label: 'Apple'),
              DropdownMenuEntry(value: 'Banana', label: 'Banana'),
              DropdownMenuEntry(value: 'Cherry', label: 'Cherry'),
            ],
          ),
        ],
      ),
    );
  }
}
