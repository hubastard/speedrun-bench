// A screen closing as React Navigation's JavaScript stack closed one before version 7
// (@react-navigation/stack 6, CardContainer): the closing screen leaves the accessibility tree
// at once, but stays mounted and takes touches while it fades out, until the animation's end
// reaches JavaScript and removes it; the screen under it ignores touches until then. With the
// JavaScript thread busy right after the choice, as a debug bundle on a CI runner keeps it
// (here 800 ms of work, in the task after the choice's), the tree shows the form while a tap
// still goes to the faded-out list (Android: a view at opacity 0 takes touches) or nowhere
// (iOS: UIKit passes over it, and the form ignores the touch). The amount field is where the
// list's last rows are.
import React, { useRef, useState } from 'react';
import { Animated, Keyboard, Pressable, StyleSheet, Text, TextInput, View } from 'react-native';

import { s, Screen, useColors } from '../ui';

const ACCOUNTS = ['Chequing', 'Savings', 'Travel', 'Business', 'Credit card'];
const ROW = 70;
const BUSY_MS = 800;
const FADE_MS = 250;

// Blocks the JavaScript thread, as a slow device's rendering and queries do.
function busy(ms: number) {
  const end = Date.now() + ms;
  while (Date.now() < end) {}
}

export function Transitions() {
  const c = useColors();
  const [to, setTo] = useState<string>();
  const [amount, setAmount] = useState('');
  const [list, setList] = useState<'open' | 'closing' | 'closed'>('closed');
  const opacity = useRef(new Animated.Value(0)).current;

  const open = () => {
    Keyboard.dismiss(); // as a picker does
    opacity.setValue(1);
    setList('open');
  };
  const choose = (name: string) => {
    setTo(name);
    setList('closing');
    Animated.timing(opacity, { toValue: 0, duration: FADE_MS, useNativeDriver: true }).start(() => setList('closed'));
    setTimeout(() => busy(BUSY_MS), 0);
  };

  return (
    <Screen title="Transitions" scroll={false}>
      <View style={{ flex: 1 }}>
        <View testID="transfer-form" style={{ flex: 1 }} pointerEvents={list === 'closed' ? 'box-none' : 'none'}
          accessibilityElementsHidden={list === 'open'} importantForAccessibility={list === 'open' ? 'no-hide-descendants' : 'auto'}>
          <Pressable testID="transfer-pick" accessibilityRole="button" onPress={open}
            style={{ height: ROW, justifyContent: 'center', paddingHorizontal: 16 }}>
            <Text style={{ color: c.text, fontSize: 16 }}>{to ? `To: ${to}` : 'To: Select an account'}</Text>
          </Pressable>
          {/* Down to the list's fourth row: the field is where "Business" and "Credit card" are. */}
          <View style={{ height: ROW * 3 - 20 }} />
          <TextInput testID="transfer-amount" placeholder="Amount" placeholderTextColor={c.muted} keyboardType="number-pad"
            value={amount} onChangeText={setAmount}
            style={[s.field, { color: c.text, borderColor: c.border, marginHorizontal: 16, height: ROW + 40 }]} />
          <Text testID="transfer-summary" style={{ color: c.text, margin: 16 }}>{`Send ${amount || 'nothing'} to ${to ?? 'nobody'}`}</Text>
        </View>
        {list !== 'closed' ? (
          <Animated.View testID="account-list" style={[StyleSheet.absoluteFill, { opacity, backgroundColor: c.bg }]}
            accessibilityElementsHidden={list === 'closing'} importantForAccessibility={list === 'closing' ? 'no-hide-descendants' : 'auto'}>
            {ACCOUNTS.map((name) => (
              <Pressable key={name} testID={`account-${name}`} accessibilityRole="button" onPress={() => choose(name)}
                style={{ height: ROW, justifyContent: 'center', paddingHorizontal: 16, borderBottomWidth: 1, borderColor: c.border }}>
                <Text style={{ color: c.text, fontSize: 16 }}>{`Account ${name}`}</Text>
              </Pressable>
            ))}
          </Animated.View>
        ) : null}
      </View>
    </Screen>
  );
}
