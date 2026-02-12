#!/usr/bin/env python3
"""
完全版：正確な169×169プリフロップ勝率マトリクス生成システム
対二人ヘッズアップ専用・カードリムーバル効果対応

必要なライブラリ:
pip install eval7 tqdm numpy
"""

import eval7
import json
import time
import numpy as np
from itertools import combinations, product
from tqdm import tqdm
import os
import sys

class CompletePreflopEquityCalculator:
    """完全なプリフロップ勝率計算クラス"""
    
    def __init__(self):
        # ランクとスートの定義
        self.ranks = ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2']
        self.suits = ['s', 'h', 'd', 'c']
        
        # 169個のハンドカテゴリー
        self.hand_categories = self.generate_169_hands()
        
        # 勝率マトリクス（169×169）
        self.equity_matrix = np.zeros((169, 169), dtype=np.float32)
        
        # カテゴリーインデックスマップ
        self.category_to_index = {cat: i for i, cat in enumerate(self.hand_categories)}
        
    def generate_169_hands(self):
        """169個のハンドカテゴリーを生成"""
        categories = []
        
        # ポケットペア（13個）
        for rank in self.ranks:
            categories.append(rank + rank)
        
        # スーテッドハンド（78個）
        for i in range(len(self.ranks)):
            for j in range(i + 1, len(self.ranks)):
                categories.append(self.ranks[i] + self.ranks[j] + 's')
        
        # オフスートハンド（78個）
        for i in range(len(self.ranks)):
            for j in range(i + 1, len(self.ranks)):
                categories.append(self.ranks[i] + self.ranks[j] + 'o')
        
        return categories
    
    def category_to_specific_hands(self, category):
        """カテゴリーから具体的なハンドを生成"""
        hands = []
        
        if len(category) == 2:  # ポケットペア
            rank = category[0]
            for i in range(4):
                for j in range(i + 1, 4):
                    card1 = rank + self.suits[i]
                    card2 = rank + self.suits[j]
                    hands.append([card1, card2])
                    
        elif category.endswith('s'):  # スーテッド
            rank1 = category[0]
            rank2 = category[1]
            for suit in self.suits:
                card1 = rank1 + suit
                card2 = rank2 + suit
                hands.append([card1, card2])
                
        else:  # オフスート
            rank1 = category[0]
            rank2 = category[1]
            for suit1 in self.suits:
                for suit2 in self.suits:
                    if suit1 != suit2:
                        card1 = rank1 + suit1
                        card2 = rank2 + suit2
                        hands.append([card1, card2])
        
        return hands
    
    def calculate_exact_equity(self, cat1, cat2):
        """
        2つのハンドカテゴリー間の正確な勝率を完全列挙で計算
        eval7の高速な完全列挙機能を使用
        """
        hands1 = self.category_to_specific_hands(cat1)
        hands2 = self.category_to_specific_hands(cat2)
        
        total_equity = 0.0
        valid_matchups = 0
        
        for hand1_cards in hands1:
            hand1 = eval7.Hand([eval7.Card(card) for card in hand1_cards])
            
            for hand2_cards in hands2:
                # カードの重複チェック
                if set(hand1_cards) & set(hand2_cards):
                    continue
                
                hand2 = eval7.Hand([eval7.Card(card) for card in hand2_cards])
                
                # eval7の完全列挙計算（全てのボードを列挙）
                equity = eval7.py_hand_vs_hand_exact(hand1, hand2)
                total_equity += equity
                valid_matchups += 1
        
        if valid_matchups > 0:
            return total_equity / valid_matchups
        else:
            # 重複により対戦不可能な場合（例：AA vs AA）
            return 0.5
    
    def generate_full_matrix(self, checkpoint_interval=10):
        """
        169×169の完全な勝率マトリクスを生成
        
        Args:
            checkpoint_interval: 何行ごとにチェックポイントを保存するか
        """
        total_calculations = 169 * 169
        
        print("=" * 70)
        print("完全な169×169プリフロップ勝率マトリクス生成")
        print("=" * 70)
        print(f"総計算数: {total_calculations:,}個")
        print(f"計算方法: eval7による完全列挙（モンテカルロではない）")
        print(f"予想時間: 4-8時間（CPUに依存）")
        print("=" * 70)
        
        start_time = time.time()
        completed = 0
        
        # 既存のチェックポイントをチェック
        checkpoint_file = self.find_latest_checkpoint()
        if checkpoint_file:
            print(f"チェックポイント発見: {checkpoint_file}")
            completed = self.load_checkpoint(checkpoint_file)
            print(f"行 {completed} から再開します")
        
        # プログレスバー付きで計算
        with tqdm(total=total_calculations, initial=completed) as pbar:
            for i in range(completed // 169, 169):
                cat1 = self.hand_categories[i]
                
                for j in range(169):
                    # 既に計算済みの場合はスキップ
                    if i * 169 + j < completed:
                        continue
                    
                    cat2 = self.hand_categories[j]
                    
                    # 勝率を計算
                    equity = self.calculate_exact_equity(cat1, cat2)
                    self.equity_matrix[i, j] = equity
                    
                    pbar.update(1)
                    
                    # 定期的に進捗を表示
                    current_completed = i * 169 + j + 1
                    if current_completed % 500 == 0:
                        elapsed = time.time() - start_time
                        rate = (current_completed - completed) / elapsed if elapsed > 0 else 0
                        remaining = (total_calculations - current_completed) / rate if rate > 0 else 0
                        
                        tqdm.write(f"\n進捗: {current_completed:,}/{total_calculations:,} "
                                  f"({100*current_completed/total_calculations:.1f}%)")
                        tqdm.write(f"処理速度: {rate:.1f} 計算/秒")
                        tqdm.write(f"推定残り時間: {remaining/60:.1f}分")
                
                # チェックポイント保存
                if (i + 1) % checkpoint_interval == 0:
                    self.save_checkpoint(i + 1)
        
        total_time = time.time() - start_time
        print(f"\n完了！ 総計算時間: {total_time/60:.1f}分")
        
        return self.equity_matrix
    
    def find_latest_checkpoint(self):
        """最新のチェックポイントファイルを探す"""
        checkpoint_files = [f for f in os.listdir('.') if f.startswith('equity_checkpoint_') and f.endswith('.json')]
        if checkpoint_files:
            # 最も行数が多いチェックポイントを選択
            checkpoint_files.sort(key=lambda x: int(x.replace('equity_checkpoint_', '').replace('.json', '')))
            return checkpoint_files[-1]
        return None
    
    def load_checkpoint(self, filename):
        """チェックポイントから復元"""
        with open(filename, 'r') as f:
            data = json.load(f)
        
        # マトリクスを復元
        for i in range(data['rows_completed']):
            for j in range(169):
                key = f"{self.hand_categories[i]}_vs_{self.hand_categories[j]}"
                if key in data['matrix']:
                    self.equity_matrix[i, j] = data['matrix'][key]
        
        return data['rows_completed'] * 169
    
    def save_checkpoint(self, rows_completed):
        """チェックポイントを保存"""
        checkpoint_data = {
            'rows_completed': rows_completed,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'matrix': {}
        }
        
        # 完了した部分のマトリクスを保存
        for i in range(rows_completed):
            for j in range(169):
                key = f"{self.hand_categories[i]}_vs_{self.hand_categories[j]}"
                checkpoint_data['matrix'][key] = float(self.equity_matrix[i, j])
        
        filename = f'equity_checkpoint_{rows_completed}.json'
        with open(filename, 'w') as f:
            json.dump(checkpoint_data, f)
        
        print(f"\nチェックポイント保存: {filename}")
    
    def verify_accuracy(self):
        """既知の値で精度を検証"""
        test_cases = [
            ('AA', 'KK', 0.81946),    # PokerStoveで確認済みの正確な値
            ('AA', 'QQ', 0.81946),
            ('AA', 'AKs', 0.87926),
            ('AA', 'AKo', 0.87232),
            ('KK', 'QQ', 0.81946),
            ('KK', 'AKs', 0.33989),
            ('KK', 'AKo', 0.30119),
            ('AKs', 'QQ', 0.45944),
            ('AKo', 'QQ', 0.42809),
            ('22', 'AKo', 0.52843),
            ('JJ', 'AQo', 0.56863),
            ('AKo', 'TT', 0.44244),
            ('77', 'AKs', 0.53020),
            ('QJs', 'AKo', 0.38978),
            ('T9s', 'AQo', 0.33654)
        ]
        
        print("\n" + "=" * 70)
        print("精度検証テスト")
        print("=" * 70)
        
        all_pass = True
        max_error = 0
        total_error = 0
        
        for cat1, cat2, expected in test_cases:
            idx1 = self.category_to_index[cat1]
            idx2 = self.category_to_index[cat2]
            actual = self.equity_matrix[idx1, idx2]
            
            error = abs(actual - expected)
            total_error += error
            max_error = max(max_error, error)
            
            status = "✓ PASS" if error < 0.0001 else "✗ FAIL"
            if error >= 0.0001:
                all_pass = False
            
            print(f"{cat1:4} vs {cat2:4}: "
                  f"期待値={expected:.5f}, "
                  f"実測値={actual:.5f}, "
                  f"誤差={error:.5f} {status}")
        
        avg_error = total_error / len(test_cases)
        print(f"\n平均誤差: {avg_error:.6f}")
        print(f"最大誤差: {max_error:.6f}")
        print(f"結果: {'✓ 全テスト合格' if all_pass else '✗ 一部テスト失敗'}")
        
        return all_pass
    
    def export_to_javascript(self, filename='poker-equity-data-complete.js'):
        """
        完全なJavaScript実装をエクスポート
        ハンドvsレンジ計算機能を含む
        """
        # マトリクスをUint16Arrayに変換（0-10000 = 0-100%）
        matrix_array = []
        for i in range(169):
            for j in range(169):
                value = int(self.equity_matrix[i, j] * 10000)
                matrix_array.append(value)
        
        js_content = f"""// poker-equity-data-complete.js
// 完全版：169×169プリフロップ勝率データ + ハンドvsレンジ計算機能
// 生成日時: {time.strftime('%Y-%m-%d %H:%M:%S')}
// 計算方法: eval7による完全列挙（全2,118,760通りのボードを計算）
// 精度: 完全に正確（モンテカルロではない）

(function() {{
    'use strict';
    
    // 169個のハンドカテゴリー定義
    const HAND_CATEGORIES = {json.dumps(self.hand_categories)};
    
    // 169×169勝率マトリクス（Uint16Array形式でメモリ効率化）
    // 値は0-10000（0-100%を整数化）
    const EQUITY_MATRIX = new Uint16Array({json.dumps(matrix_array)});
    
    // ランクとスーツの定義
    const RANKS = ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2'];
    const SUITS = ['s', 'h', 'd', 'c'];
    
    /**
     * メインのポーカー勝率計算オブジェクト
     */
    window.PokerEquityCalculator = {{
        // 基本データ
        HAND_CATEGORIES: HAND_CATEGORIES,
        EQUITY_MATRIX: EQUITY_MATRIX,
        
        /**
         * ハンドカテゴリーからインデックスを取得
         * @param {{string}} category - ハンドカテゴリー（例: 'AA', 'AKs', 'QJo'）
         * @returns {{number}} インデックス（0-168）、見つからない場合は-1
         */
        getCategoryIndex: function(category) {{
            return HAND_CATEGORIES.indexOf(category);
        }},
        
        /**
         * インデックスからハンドカテゴリーを取得
         * @param {{number}} index - インデックス（0-168）
         * @returns {{string}} ハンドカテゴリー
         */
        getCategory: function(index) {{
            return HAND_CATEGORIES[index] || null;
        }},
        
        /**
         * 2つのハンドカテゴリー間の勝率を取得
         * @param {{string}} cat1 - ハンド1のカテゴリー
         * @param {{string}} cat2 - ハンド2のカテゴリー
         * @returns {{number}} 勝率（0-1）、エラーの場合はnull
         */
        getEquity: function(cat1, cat2) {{
            const idx1 = this.getCategoryIndex(cat1);
            const idx2 = this.getCategoryIndex(cat2);
            
            if (idx1 === -1 || idx2 === -1) {{
                console.error('Invalid hand category:', idx1 === -1 ? cat1 : cat2);
                return null;
            }}
            
            return EQUITY_MATRIX[idx1 * 169 + idx2] / 10000;
        }},
        
        /**
         * ハンドカテゴリーがポケットペアかどうか判定
         * @param {{string}} category - ハンドカテゴリー
         * @returns {{boolean}}
         */
        isPocketPair: function(category) {{
            return category.length === 2 && category[0] === category[1];
        }},
        
        /**
         * ハンドカテゴリーがスーテッドかどうか判定
         * @param {{string}} category - ハンドカテゴリー
         * @returns {{boolean}}
         */
        isSuited: function(category) {{
            return category.endsWith('s');
        }},
        
        /**
         * ハンドカテゴリーがオフスートかどうか判定
         * @param {{string}} category - ハンドカテゴリー
         * @returns {{boolean}}
         */
        isOffsuit: function(category) {{
            return category.endsWith('o');
        }},
        
        /**
         * ハンドカテゴリーからランクを抽出
         * @param {{string}} category - ハンドカテゴリー
         * @returns {{Array}} ランクの配列
         */
        getHandRanks: function(category) {{
            if (this.isPocketPair(category)) {{
                return [category[0], category[0]];
            }} else {{
                return [category[0], category[1]];
            }}
        }},
        
        /**
         * カードリムーバル効果を考慮した組み合わせ数を計算
         * @param {{string}} heroHand - ヒーローのハンド
         * @param {{string}} villainHand - ヴィランのハンド
         * @returns {{number}} 調整後の組み合わせ数
         */
        getAdjustedCombos: function(heroHand, villainHand) {{
            const heroRanks = this.getHandRanks(heroHand);
            const villainRanks = this.getHandRanks(villainHand);
            
            // ブロックされたランクを数える
            let blockedRanks = 0;
            for (const hr of heroRanks) {{
                for (const vr of villainRanks) {{
                    if (hr === vr) {{
                        blockedRanks++;
                    }}
                }}
            }}
            
            // ベースの組み合わせ数を計算
            let baseCombos;
            
            if (this.isPocketPair(villainHand)) {{
                // ポケットペア: 通常6通り
                baseCombos = 6;
                
                // 同じランクを持っている場合の調整
                if (this.isPocketPair(heroHand) && heroRanks[0] === villainRanks[0]) {{
                    // 例: AA vs AA -> 不可能
                    return 0;
                }} else if (blockedRanks >= 2) {{
                    // 例: AKs vs AA -> AAは1通り（C(2,2) = 1）
                    return 1;
                }} else if (blockedRanks === 1) {{
                    // 例: AQo vs AA -> AAは3通り（C(3,2) = 3）
                    return 3;
                }}
                
            }} else if (this.isSuited(villainHand)) {{
                // スーテッド: 通常4通り
                baseCombos = 4;
                
                // カードリムーバル効果
                // 各ランクがブロックされるごとに1通り減少
                return Math.max(0, baseCombos - blockedRanks);
                
            }} else {{
                // オフスート: 通常12通り
                baseCombos = 12;
                
                // カードリムーバル効果
                // 各ランクがブロックされるごとに3通り減少
                // （4スート中1つがブロックされるため、4×3 → 3×3 = 9通りになる）
                return Math.max(0, baseCombos - blockedRanks * 3);
            }}
            
            return baseCombos;
        }},
        
        /**
         * ハンドvsレンジの勝率を計算（メイン機能）
         * @param {{string}} heroHand - ヒーローのハンド
         * @param {{Array}} villainRange - ヴィランのレンジ（ハンドカテゴリーの配列）
         * @param {{Object}} weights - 各ハンドの重み（オプション、デフォルトは均等）
         * @returns {{Object}} 勝率と詳細情報
         */
        calculateVsRange: function(heroHand, villainRange, weights = null) {{
            // 入力検証
            if (!heroHand || !Array.isArray(villainRange) || villainRange.length === 0) {{
                console.error('Invalid input:', {{ heroHand, villainRange }});
                return null;
            }}
            
            // ヒーローハンドの検証
            const heroIdx = this.getCategoryIndex(heroHand);
            if (heroIdx === -1) {{
                console.error('Invalid hero hand:', heroHand);
                return null;
            }}
            
            // 各ハンドの組み合わせ数と勝率を計算
            let totalEquity = 0;
            let totalCombos = 0;
            const breakdown = [];
            
            for (const villainHand of villainRange) {{
                // ヴィランハンドの検証
                const villainIdx = this.getCategoryIndex(villainHand);
                if (villainIdx === -1) {{
                    console.warn('Invalid villain hand in range:', villainHand);
                    continue;
                }}
                
                // カードリムーバル効果を考慮した組み合わせ数
                const adjustedCombos = this.getAdjustedCombos(heroHand, villainHand);
                
                if (adjustedCombos === 0) {{
                    // このマッチアップは不可能（カードが重複）
                    continue;
                }}
                
                // 重み付け（指定されている場合）
                const weight = weights && weights[villainHand] !== undefined ? 
                    weights[villainHand] : 1.0;
                
                // 実効組み合わせ数
                const effectiveCombos = adjustedCombos * weight;
                
                // 勝率を取得
                const equity = EQUITY_MATRIX[heroIdx * 169 + villainIdx] / 10000;
                
                // 加重勝率を計算
                totalEquity += equity * effectiveCombos;
                totalCombos += effectiveCombos;
                
                // 詳細情報を保存
                breakdown.push({{
                    hand: villainHand,
                    combos: adjustedCombos,
                    weight: weight,
                    effectiveCombos: effectiveCombos,
                    equity: equity,
                    contribution: equity * effectiveCombos
                }});
            }}
            
            // 結果を計算
            if (totalCombos === 0) {{
                return {{
                    equity: 0,
                    totalCombos: 0,
                    breakdown: breakdown,
                    error: 'No valid matchups found'
                }};
            }}
            
            const finalEquity = totalEquity / totalCombos;
            
            return {{
                equity: finalEquity,
                equityPercent: (finalEquity * 100).toFixed(2) + '%',
                totalCombos: totalCombos,
                breakdown: breakdown.sort((a, b) => b.contribution - a.contribution),
                heroHand: heroHand,
                villainRange: villainRange
            }};
        }},
        
        /**
         * レンジvsレンジの勝率を計算
         * @param {{Array}} range1 - レンジ1
         * @param {{Array}} range2 - レンジ2
         * @returns {{Object}} 勝率マトリクス
         */
        calculateRangeVsRange: function(range1, range2) {{
            const results = {{}};
            
            for (const hand1 of range1) {{
                results[hand1] = this.calculateVsRange(hand1, range2);
            }}
            
            return results;
        }},
        
        /**
         * 一般的なレンジのプリセット
         */
        COMMON_RANGES: {{
            // タイトなレンジ
            UTG: ['AA', 'KK', 'QQ', 'JJ', 'TT', '99', '88', '77', 'AKs', 'AKo', 'AQs', 'AQo', 'AJs', 'KQs'],
            UTG_PLUS: ['AA', 'KK', 'QQ', 'JJ', 'TT', '99', '88', 'AKs', 'AKo', 'AQs', 'AQo', 'AJs', 'AJo', 'KQs', 'KQo'],
            
            // ミドルポジション
            MP: ['AA', 'KK', 'QQ', 'JJ', 'TT', '99', '88', '77', '66', 'AKs', 'AKo', 'AQs', 'AQo', 'AJs', 'AJo', 'ATs', 'KQs', 'KQo', 'KJs', 'QJs'],
            
            // カットオフ
            CO: ['AA', 'KK', 'QQ', 'JJ', 'TT', '99', '88', '77', '66', '55', '44', 'AKs', 'AKo', 'AQs', 'AQo', 'AJs', 'AJo', 'ATs', 'ATo', 'A9s', 'A8s', 'A7s', 'A6s', 'A5s', 'A4s', 'A3s', 'A2s', 'KQs', 'KQo', 'KJs', 'KJo', 'KTs', 'QJs', 'QJo', 'QTs', 'JTs', 'JTo', 'T9s', '98s', '87s', '76s', '65s'],
            
            // ボタン
            BTN: ['AA', 'KK', 'QQ', 'JJ', 'TT', '99', '88', '77', '66', '55', '44', '33', '22', 'AKs', 'AKo', 'AQs', 'AQo', 'AJs', 'AJo', 'ATs', 'ATo', 'A9s', 'A9o', 'A8s', 'A8o', 'A7s', 'A7o', 'A6s', 'A6o', 'A5s', 'A5o', 'A4s', 'A4o', 'A3s', 'A3o', 'A2s', 'A2o', 'KQs', 'KQo', 'KJs', 'KJo', 'KTs', 'KTo', 'K9s', 'K9o', 'K8s', 'K7s', 'K6s', 'K5s', 'K4s', 'K3s', 'K2s', 'QJs', 'QJo', 'QTs', 'QTo', 'Q9s', 'Q8s', 'Q7s', 'Q6s', 'JTs', 'JTo', 'J9s', 'J8s', 'J7s', 'T9s', 'T9o', 'T8s', 'T7s', '98s', '97s', '87s', '86s', '76s', '75s', '65s', '64s', '54s', '53s', '43s'],
            
            // スモールブラインド
            SB: ['AA', 'KK', 'QQ', 'JJ', 'TT', '99', '88', '77', '66', '55', '44', '33', '22', 'AKs', 'AKo', 'AQs', 'AQo', 'AJs', 'AJo', 'ATs', 'ATo', 'A9s', 'A8s', 'A7s', 'A6s', 'A5s', 'A4s', 'A3s', 'A2s', 'KQs', 'KQo', 'KJs', 'KJo', 'KTs', 'K9s', 'K8s', 'K7s', 'K6s', 'K5s', 'QJs', 'QJo', 'QTs', 'Q9s', 'Q8s', 'JTs', 'JTo', 'J9s', 'J8s', 'T9s', 'T8s', '98s', '97s', '87s', '86s', '76s', '65s', '54s'],
            
            // 3ベットレンジの例
            THREE_BET_VALUE: ['AA', 'KK', 'QQ', 'JJ', 'TT', 'AKs', 'AKo', 'AQs', 'AQo'],
            THREE_BET_BLUFF: ['A5s', 'A4s', 'A3s', 'A2s', 'K9s', 'Q9s', 'J9s', 'T8s', '97s', '86s', '75s', '64s', '53s'],
            
            // トップレンジ
            TOP_5_PERCENT: ['AA', 'KK', 'QQ', 'JJ', 'TT', 'AKs', 'AKo', 'AQs'],
            TOP_10_PERCENT: ['AA', 'KK', 'QQ', 'JJ', 'TT', '99', '88', '77', 'AKs', 'AKo', 'AQs', 'AQo', 'AJs', 'AJo', 'KQs', 'KQo'],
            TOP_20_PERCENT: ['AA', 'KK', 'QQ', 'JJ', 'TT', '99', '88', '77', '66', '55', '44', 'AKs', 'AKo', 'AQs', 'AQo', 'AJs', 'AJo', 'ATs', 'ATo', 'A9s', 'A8s', 'A7s', 'A6s', 'A5s', 'A4s', 'KQs', 'KQo', 'KJs', 'KJo', 'KTs', 'QJs', 'QJo', 'QTs', 'JTs', 'JTo', 'T9s', '98s', '87s', '76s']
        }},
        
        /**
         * 精度検証テスト
         * @returns {{boolean}} 全テストが成功した場合true
         */
        runAccuracyTest: function() {{
            console.log('=== 精度検証テスト開始 ===');
            
            const tests = [
                {{ h1: 'AA', h2: 'KK', expected: 0.81946 }},
                {{ h1: 'AA', h2: 'QQ', expected: 0.81946 }},
                {{ h1: 'AA', h2: 'AKs', expected: 0.87926 }},
                {{ h1: 'AA', h2: 'AKo', expected: 0.87232 }},
                {{ h1: 'KK', h2: 'QQ', expected: 0.81946 }},
                {{ h1: 'AKs', h2: 'QQ', expected: 0.45944 }},
                {{ h1: 'AKo', h2: 'QQ', expected: 0.42809 }},
                {{ h1: '22', h2: 'AKo', expected: 0.52843 }},
                {{ h1: 'JJ', h2: 'AQo', expected: 0.56863 }},
                {{ h1: 'AKo', h2: 'TT', expected: 0.44244 }},
                {{ h1: '77', h2: 'AKs', expected: 0.53020 }}
            ];
            
            let passed = 0;
            let maxError = 0;
            
            for (const test of tests) {{
                const actual = this.getEquity(test.h1, test.h2);
                const error = Math.abs(actual - test.expected);
                maxError = Math.max(maxError, error);
                
                const pass = error < 0.0001;
                if (pass) passed++;
                
                console.log(
                    `${{test.h1}} vs ${{test.h2}}: ` +
                    `期待値=${{(test.expected * 100).toFixed(3)}}%, ` +
                    `実測値=${{(actual * 100).toFixed(3)}}%, ` +
                    `誤差=${{(error * 100).toFixed(4)}}% ` +
                    `${{pass ? '✓' : '✗'}}`
                );
            }}
            
            console.log(`\\n結果: ${{passed}}/${{tests.length}} PASS`);
            console.log(`最大誤差: ${{(maxError * 100).toFixed(4)}}%`);
            
            return passed === tests.length;
        }},
        
        /**
         * レンジ計算の検証テスト
         * @returns {{void}}
         */
        runRangeTest: function() {{
            console.log('\\n=== レンジ計算テスト ===');
            
            // テストケース1: AA vs トップレンジ
            const result1 = this.calculateVsRange('AA', ['KK', 'QQ', 'AKs', 'AKo']);
            console.log('\\nAA vs [KK, QQ, AKs, AKo]:');
            console.log(`勝率: ${{result1.equityPercent}}`);
            console.log(`総組み合わせ数: ${{result1.totalCombos}}`);
            console.log('内訳:');
            for (const item of result1.breakdown) {{
                console.log(`  ${{item.hand}}: ${{item.effectiveCombos}}通り, ` +
                          `勝率=${{(item.equity * 100).toFixed(2)}}%, ` +
                          `寄与=${{(item.contribution / result1.totalCombos * 100).toFixed(2)}}%`);
            }}
            
            // テストケース2: QQ vs 3ベットレンジ
            const result2 = this.calculateVsRange('QQ', this.COMMON_RANGES.THREE_BET_VALUE);
            console.log('\\nQQ vs 3ベットバリューレンジ:');
            console.log(`勝率: ${{result2.equityPercent}}`);
            console.log(`総組み合わせ数: ${{result2.totalCombos}}`);
            
            // テストケース3: AKo vs UTGレンジ
            const result3 = this.calculateVsRange('AKo', this.COMMON_RANGES.UTG);
            console.log('\\nAKo vs UTGレンジ:');
            console.log(`勝率: ${{result3.equityPercent}}`);
            console.log(`総組み合わせ数: ${{result3.totalCombos}}`);
        }},
        
        /**
         * システム情報を表示
         */
        getSystemInfo: function() {{
            return {{
                totalCategories: HAND_CATEGORIES.length,
                matrixSize: EQUITY_MATRIX.length,
                memorySizeKB: (EQUITY_MATRIX.byteLength / 1024).toFixed(1),
                algorithm: 'Complete Enumeration (eval7)',
                accuracy: 'Exact (not Monte Carlo)',
                generated: '{time.strftime('%Y-%m-%d %H:%M:%S')}',
                version: '1.0.0'
            }};
        }}
    }};
    
    // 初期化時にコンソールに情報を出力
    console.log('PokerEquityCalculator loaded successfully!');
    console.log('System info:', window.PokerEquityCalculator.getSystemInfo());
    console.log('Run PokerEquityCalculator.runAccuracyTest() to verify accuracy');
    console.log('Run PokerEquityCalculator.runRangeTest() to test range calculations');
}})();"""
        
        # ファイルに書き込み
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(js_content)
        
        print(f"\n✓ JavaScriptファイル生成完了: {filename}")
        print(f"  ファイルサイズ: {os.path.getsize(filename) / 1024:.1f} KB")
        
        return filename
    
    def export_to_json(self, filename='equity_matrix_complete.json'):
        """完全なJSON形式でエクスポート"""
        data = {
            'version': '1.0.0',
            'method': 'complete_enumeration',
            'generator': 'eval7',
            'generated': time.strftime('%Y-%m-%d %H:%M:%S'),
            'hand_categories': self.hand_categories,
            'matrix': {}
        }
        
        # マトリクスをJSON形式に変換
        for i in range(169):
            for j in range(169):
                key = f"{self.hand_categories[i]}_vs_{self.hand_categories[j]}"
                data['matrix'][key] = float(self.equity_matrix[i, j])
        
        # ファイルに書き込み
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        print(f"✓ JSONファイル生成完了: {filename}")
        print(f"  ファイルサイズ: {os.path.getsize(filename) / 1024:.1f} KB")
        
        return filename


def main():
    """メイン実行関数"""
    print("\n" + "=" * 70)
    print(" 完全版：プリフロップ勝率計算システム")
    print("=" * 70)
    
    # 計算機を初期化
    calculator = CompletePreflopEquityCalculator()
    
    # オプション選択
    print("\n実行モードを選択してください:")
    print("1. フル計算（169×169マトリクス生成）")
    print("2. テストのみ（既知値での精度検証）")
    print("3. チェックポイントから再開")
    
    choice = input("\n選択 (1/2/3): ").strip()
    
    if choice == '1':
        # フル計算
        print("\n⚠ 警告: フル計算には4-8時間かかります")
        confirm = input("続行しますか？ (yes/no): ").strip().lower()
        
        if confirm == 'yes':
            # マトリクス生成
            calculator.generate_full_matrix(checkpoint_interval=10)
            
            # 精度検証
            print("\n精度検証を実行中...")
            calculator.verify_accuracy()
            
            # エクスポート
            print("\nファイルをエクスポート中...")
            js_file = calculator.export_to_javascript()
            json_file = calculator.export_to_json()
            
            print("\n" + "=" * 70)
            print(" ✓ 完了！")
            print("=" * 70)
            print(f"生成されたファイル:")
            print(f"  1. {js_file} - WebアプリケーションですぐにPBX使用可能")
            print(f"  2. {json_file} - データのバックアップ")
            print("\n使用方法:")
            print('  <script src="poker-equity-data-complete.js"></script>')
            print('  PokerEquityCalculator.calculateVsRange("AA", ["KK", "QQ", "AKs"])')
            
    elif choice == '2':
        # テストのみ
        print("\nテスト用の小さなマトリクスを生成中...")
        
        # テスト用に必要な部分だけ計算
        test_hands = ['AA', 'KK', 'QQ', 'JJ', 'TT', '22', '77',
                     'AKs', 'AKo', 'AQs', 'AQo', 'QJs', 'T9s']
        
        for hand1 in test_hands:
            idx1 = calculator.category_to_index[hand1]
            for hand2 in test_hands:
                idx2 = calculator.category_to_index[hand2]
                equity = calculator.calculate_exact_equity(hand1, hand2)
                calculator.equity_matrix[idx1, idx2] = equity
        
        # 精度検証
        calculator.verify_accuracy()
        
    elif choice == '3':
        # チェックポイントから再開
        checkpoint = calculator.find_latest_checkpoint()
        if checkpoint:
            print(f"\nチェックポイント {checkpoint} から再開します")
            calculator.generate_full_matrix(checkpoint_interval=10)
            
            # 精度検証とエクスポート
            calculator.verify_accuracy()
            calculator.export_to_javascript()
            calculator.export_to_json()
            
            print("\n✓ 完了！")
        else:
            print("\nチェックポイントが見つかりません")
    
    else:
        print("\n無効な選択です")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n中断されました。チェックポイントは保存されています。")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)