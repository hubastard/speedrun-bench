import 'package:flutter/material.dart';

/// A long lazy list (rows built as they scroll in), rows with a title and a subtitle (Flutter
/// merges a ListTile's texts into one node), pull to refresh, and a detail screen pushed with
/// the platform's transition and a Hero.
class Feed extends StatefulWidget {
  const Feed({super.key});

  @override
  State<Feed> createState() => _FeedState();
}

class _FeedState extends State<Feed> {
  final items = [for (var i = 1; i <= 120; i++) 'Article $i'];
  int refreshes = 0;

  Future<void> refresh() async {
    await Future<void>.delayed(const Duration(milliseconds: 800));
    setState(() => items.insert(0, 'Fresh article ${++refreshes}'));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Feed')),
      body: RefreshIndicator(
        onRefresh: refresh,
        child: ListView.builder(
          itemCount: items.length,
          itemBuilder: (context, i) => ListTile(
            leading: Hero(
              tag: items[i],
              child: CircleAvatar(child: Text('${i % 9 + 1}')),
            ),
            title: Text(items[i]),
            subtitle: Text('By author ${i % 7 + 1}'),
            onTap: () => Navigator.of(
              context,
            ).push(MaterialPageRoute(builder: (_) => Article(title: items[i]))),
          ),
        ),
      ),
    );
  }
}

class Article extends StatefulWidget {
  const Article({super.key, required this.title});

  final String title;

  @override
  State<Article> createState() => _ArticleState();
}

class _ArticleState extends State<Article> {
  int likes = 0;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.title),
        actions: [
          IconButton(
            tooltip: 'Like',
            icon: const Icon(Icons.favorite_border),
            onPressed: () => setState(() => likes++),
          ),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Hero(
              tag: widget.title,
              child: const CircleAvatar(radius: 40, child: Icon(Icons.article)),
            ),
            const SizedBox(height: 16),
            Text('Likes: $likes'),
            const SizedBox(height: 8),
            const Text(
              'Lorem ipsum dolor sit amet, consectetur adipiscing elit.',
            ),
          ],
        ),
      ),
    );
  }
}
