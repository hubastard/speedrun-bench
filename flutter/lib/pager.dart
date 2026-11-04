import 'package:flutter/material.dart';

/// Sideways paging: an onboarding PageView turned by swipes or by its button, and tabs whose
/// pages swipe (TabBarView).
class Pager extends StatefulWidget {
  const Pager({super.key});

  @override
  State<Pager> createState() => _PagerState();
}

class _PagerState extends State<Pager> {
  final pages = PageController();
  int page = 0;
  static const titles = [
    'Welcome aboard',
    'Track your runs',
    'Share your times',
  ];

  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: 3,
      child: Scaffold(
        appBar: AppBar(title: const Text('Pager')),
        body: Column(
          children: [
            SizedBox(
              height: 220,
              child: PageView(
                controller: pages,
                onPageChanged: (p) => setState(() => page = p),
                children: [
                  for (final t in titles)
                    Card(
                      margin: const EdgeInsets.all(16),
                      child: Center(
                        child: Text(
                          t,
                          style: Theme.of(context).textTheme.headlineSmall,
                        ),
                      ),
                    ),
                ],
              ),
            ),
            Text('Page ${page + 1} of 3'),
            TextButton(
              onPressed: page < 2
                  ? () => pages.nextPage(
                      duration: const Duration(milliseconds: 300),
                      curve: Curves.easeOut,
                    )
                  : null,
              child: const Text('Next'),
            ),
            const TabBar(
              tabs: [
                Tab(text: 'Inbox'),
                Tab(text: 'Sent'),
                Tab(text: 'Drafts'),
              ],
            ),
            Expanded(
              child: TabBarView(
                children: [
                  for (final box in ['Inbox', 'Sent', 'Drafts'])
                    ListView(
                      children: [
                        for (var i = 1; i <= 3; i++)
                          ListTile(title: Text('$box message $i')),
                      ],
                    ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
