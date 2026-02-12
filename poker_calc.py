#!/usr/bin/env python3
"""
ハンド vs レンジ 正確な計算
eval7の実際のAPIに完全対応したバージョン
"""

import eval7
import itertools
import random
import time

class AccurateRangeCalculator:
    def __init__(self):
        # eval7のランク値を調査して正しくマッピング
        # eval7では: A=12, K=11, Q=10, J=9, T=8, 9=7, 8=6, 7=5, 6=4, 5=3, 4=2, 3=1, 2=0
        self.eval7_rank_map = {
            'A': 12, 'K': 11, 'Q': 10, 'J': 9, 'T': 8,
            '9': 7, '8': 6, '7': 5, '6': 4, '5': 3, '4': 2, '3': 1, '2': 0
        }
        self.rank_to_str_map = {v: k for k, v in self.eval7_rank_map.items()}
        
        # スートマップ: c=0, d=1, h=2, s=3
        self.suit_map = {'c': 0, 'd': 1, 'h': 2, 's': 3}
        self.suit_to_str_map = {v: k for k, v in self.suit_map.items()}
        
        # デッキを初期化
        self.deck = []
        for rank in ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2']:
            for suit in ['c', 'd', 'h', 's']:
                self.deck.append(eval7.Card(rank + suit))
    
    def parse_hand(self, hand_str):
        """文字列からハンドをパース"""
        cards = []
        for i in range(0, len(hand_str), 2):
            card_str = hand_str[i:i+2]
            cards.append(eval7.Card(card_str))
        return cards
    
    def card_to_str(self, card):
        """eval7.Cardを文字列に変換"""
        return self.rank_to_str_map[card.rank] + self.suit_to_str_map[card.suit]
    
    def cards_equal(self, card1, card2):
        """2つのカードが同じか判定"""
        return card1.rank == card2.rank and card1.suit == card2.suit
    
    def card_in_list(self, card, card_list):
        """カードがリストに含まれるか判定"""
        for c in card_list:
            if self.cards_equal(card, c):
                return True
        return False
    
    def parse_range_notation(self, range_str):
        """レンジ記法をパース"""
        hands = []
        parts = range_str.replace(' ', '').split(',')
        
        for part in parts:
            if '+' in part:
                hands.extend(self.expand_plus(part))
            else:
                hands.append(part)
        
        return hands
    
    def expand_plus(self, notation):
        """プラス記法を展開"""
        base = notation.replace('+', '')
        hands = []
        
        rank_order = ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2']
        
        if len(base) == 2 and base[0] == base[1]:
            # ポケットペア (例: QQ+)
            start_idx = rank_order.index(base[0])
            for i in range(0, start_idx + 1):
                hands.append(rank_order[i] * 2)
                
        elif base.endswith('s'):
            # スーテッド (例: ATs+)
            high = base[0]
            low = base[1]
            high_idx = rank_order.index(high)
            start_idx = rank_order.index(low)
            # AKsからATsのような場合
            for i in range(high_idx + 1, start_idx + 1):
                if i < len(rank_order):
                    hands.append(high + rank_order[i] + 's')
                
        elif base.endswith('o'):
            # オフスーツ (例: ATo+)
            high = base[0]
            low = base[1]
            high_idx = rank_order.index(high)
            start_idx = rank_order.index(low)
            for i in range(high_idx + 1, start_idx + 1):
                if i < len(rank_order):
                    hands.append(high + rank_order[i] + 'o')
        
        return hands
    
    def get_all_combos_for_range(self, range_str, blocked_cards):
        """
        レンジ内の全ての実際の組み合わせを列挙
        ブロッカーを正確に考慮
        """
        range_hands = self.parse_range_notation(range_str)
        all_combos = []
        
        for hand_notation in range_hands:
            if len(hand_notation) == 2 and hand_notation[0] == hand_notation[1]:
                # ポケットペア
                rank = hand_notation[0]
                rank_value = self.eval7_rank_map[rank]
                rank_cards = []
                
                # 該当ランクのカードを収集
                for card in self.deck:
                    if card.rank == rank_value and not self.card_in_list(card, blocked_cards):
                        rank_cards.append(card)
                
                # 2枚の組み合わせを生成
                for combo in itertools.combinations(rank_cards, 2):
                    all_combos.append(list(combo))
                    
            elif hand_notation.endswith('s'):
                # スーテッド
                rank1 = hand_notation[0]
                rank2 = hand_notation[1]
                for suit in ['c', 'd', 'h', 's']:
                    card1 = eval7.Card(rank1 + suit)
                    card2 = eval7.Card(rank2 + suit)
                    if not self.card_in_list(card1, blocked_cards) and not self.card_in_list(card2, blocked_cards):
                        all_combos.append([card1, card2])
                        
            elif hand_notation.endswith('o'):
                # オフスーツ
                rank1 = hand_notation[0]
                rank2 = hand_notation[1]
                for suit1 in ['c', 'd', 'h', 's']:
                    for suit2 in ['c', 'd', 'h', 's']:
                        if suit1 != suit2:
                            card1 = eval7.Card(rank1 + suit1)
                            card2 = eval7.Card(rank2 + suit2)
                            if not self.card_in_list(card1, blocked_cards) and not self.card_in_list(card2, blocked_cards):
                                all_combos.append([card1, card2])
        
        return all_combos
    
    def calculate_hand_vs_range(self, hero_hand_str, range_str, sample_boards=10000):
        """
        正確な重み付けによるハンド vs レンジ計算
        """
        hero_cards = self.parse_hand(hero_hand_str)
        
        # ブロッカーを考慮した全ての組み合わせを取得
        villain_combos = self.get_all_combos_for_range(range_str, hero_cards)
        
        if not villain_combos:
            return {'error': 'No valid combinations in range after card removal'}
        
        print(f"Hero: {hero_hand_str}")
        print(f"Range combinations after blockers: {len(villain_combos)}")
        
        # 各組み合わせの重みは均等
        combo_weight = 1.0 / len(villain_combos)
        
        total_equity = 0.0
        
        # 各villain組み合わせに対して計算
        for idx, villain_cards in enumerate(villain_combos):
            wins = 0
            ties = 0
            
            # 使用可能なカードからボードをサンプリング
            remaining = []
            for card in self.deck:
                if not self.card_in_list(card, hero_cards) and not self.card_in_list(card, villain_cards):
                    remaining.append(card)
            
            # ボードサンプリング
            boards_to_sample = min(sample_boards, 10000)
            
            for _ in range(boards_to_sample):
                board = random.sample(remaining, 5)
                
                # ハンドを評価
                hero_score = eval7.evaluate(hero_cards + board)
                villain_score = eval7.evaluate(villain_cards + board)
                
                if hero_score < villain_score:  # eval7では小さい値が強い
                    wins += 1
                elif hero_score == villain_score:
                    ties += 1
            
            matchup_equity = (wins + ties * 0.5) / boards_to_sample
            total_equity += matchup_equity * combo_weight
            
            # 進捗表示
            if (idx + 1) % 10 == 0 or idx == len(villain_combos) - 1:
                print(f"Progress: {idx + 1}/{len(villain_combos)} combinations processed", end='\r')
        
        print()  # 改行
        
        return {
            'equity': total_equity,
            'villain_combos': len(villain_combos),
            'sample_boards': sample_boards,
            'method': 'weighted_enumeration'
        }
    
    def calculate_with_timing(self, hero_hand_str, range_str, sample_boards=10000):
        """計算時間を測定しながら実行"""
        start = time.time()
        result = self.calculate_hand_vs_range(hero_hand_str, range_str, sample_boards)
        elapsed = time.time() - start
        
        if 'error' not in result:
            result['calculation_time'] = elapsed
        return result


def test_eval7_api():
    """eval7のAPIをテストして確認"""
    print("\n=== eval7 API テスト ===")
    test_cards = ['As', 'Kh', '2c']
    for card_str in test_cards:
        card = eval7.Card(card_str)
        print(f"{card_str}: rank={card.rank}, suit={card.suit}")
    print()


# メイン実行部分
if __name__ == "__main__":
    # まずeval7のAPIをテスト
    test_eval7_api()
    
    calc = AccurateRangeCalculator()
    
    print("="*60)
    print("正確なハンド vs レンジ計算")
    print("="*60)
    
    # テスト1: AA vs プレミアムレンジ
    print("\nTest 1: AsAd vs {AA,KK,QQ,AKs,AKo}")
    result = calc.calculate_with_timing(
        "AsAd",
        "AA,KK,QQ,AKs,AKo",
        sample_boards=10000
    )
    if 'error' not in result:
        print(f"Equity: {result['equity']:.4f}")
        print(f"Villain combinations: {result['villain_combos']}")
        print(f"Calculation time: {result['calculation_time']:.2f}s")
    else:
        print(f"Error: {result['error']}")
    
    # テスト2: 88 vs レンジ
    print("\nTest 2: 8h8d vs {TT+,AQs+,AQo+}")
    result = calc.calculate_with_timing(
        "8h8d",
        "TT+,AQs+,AQo+",
        sample_boards=5000
    )
    if 'error' not in result:
        print(f"Equity: {result['equity']:.4f}")
        print(f"Villain combinations: {result['villain_combos']}")
        print(f"Calculation time: {result['calculation_time']:.2f}s")
    else:
        print(f"Error: {result['error']}")
    
    # インタラクティブモード
    print("\n" + "="*60)
    print("Interactive mode (type 'quit' to exit)")
    print("Format: HAND vs RANGE")
    print("Example: AsKh vs QQ+,AKs,AKo")
    print("="*60)
    
    while True:
        user_input = input("\nEnter: ").strip()
        if user_input.lower() == 'quit':
            break
            
        try:
            parts = user_input.split(' vs ')
            if len(parts) != 2:
                print("Error: Use format 'HAND vs RANGE'")
                continue
                
            hero = parts[0].strip()
            villain_range = parts[1].strip()
            
            result = calc.calculate_with_timing(hero, villain_range, sample_boards=10000)
            
            if 'error' not in result:
                print(f"\nResults:")
                print(f"  Equity: {result['equity']:.2%}")
                print(f"  Villain combos: {result['villain_combos']}")
                print(f"  Time: {result['calculation_time']:.2f}s")
            else:
                print(f"Error: {result['error']}")
            
        except Exception as e:
            print(f"Error: {e}")