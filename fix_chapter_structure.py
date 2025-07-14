#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第5-6章のWordPressブロック構造修正スクリプト
"""

import sys
sys.path.append('/mnt/c/home/hiroshi/blog_generator/scripts')
from wordpress_update_client import WordPressUpdateClient

def fix_chapter_structure():
    """第5-6章の破綻したブロック構造を修正"""
    
    # 現在の記事を取得
    client = WordPressUpdateClient(integration_mode=True)
    current_post = client.get_post(2127)
    content = current_post.get('content', '')
    
    print(f'元の文字数: {len(content)}')
    
    # 破綻した第5-6章部分を特定
    broken_start = content.find('<p><!-- wp:heading')
    broken_end = content.find('<!-- wp:heading {"level":2} -->\n<h2 class="wp-block-heading">まとめ</h2>')
    
    if broken_start != -1 and broken_end != -1:
        print(f'破綻開始位置: {broken_start}')
        print(f'まとめ開始位置: {broken_end}')
        
        # 正しい第5-6章コンテンツを生成
        fixed_chapters = '''
<!-- wp:heading {"level":2} -->
<h2 class="wp-block-heading">第5章：挑戦する勇気 - 一歩を踏み出すために必要な心の準備</h2>
<!-- /wp:heading -->

<!-- wp:image {"id":3274,"sizeSlug":"full","linkDestination":"none"} -->
<figure class="wp-block-image size-full"><img src="https://www.ht-sw.tech/wp-content/uploads/2025/07/20250714_112453_thumbnail_unknown_chapter5.jpg" alt="第5章 サムネイル画像" class="wp-image-3274"/></figure>
<!-- /wp:image -->

<!-- wp:paragraph -->
<p>新しいことに挑戦する時、誰もが心の奥底で不安を感じるものです。挑戦する勇気とは生まれつき持っているものではなく、日々の小さな積み重ねによって育まれるものです。</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":3} -->
<h3 class="wp-block-heading">なぜ私たちは挑戦を恐れるのか</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>人間が新しい挑戦を恐れるのは自然な本能です。私が初めて転職を考えた時、10年間働いた会社を辞めることに強い不安を感じました。</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p><strong>💭 当時の私の心境</strong></p>
<!-- /wp:paragraph -->

<!-- wp:list -->
<ul>
<li>今の会社を辞めて本当に大丈夫なのか</li>
<li>新しい職場で通用するスキルはあるのか</li>
<li>家族を養っていけるのか</li>
<li>失敗したらどうしよう</li>
</ul>
<!-- /wp:list -->

<!-- wp:paragraph -->
<p>この不安こそが挑戦する勇気を育てる第一歩になることを、後になって知りました。不安は「準備が必要」「慎重に検討すべき」というサインでもあるのです。</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":3} -->
<h3 class="wp-block-heading">小さな勇気から始める実践方法</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p><strong>🌱 勇気を育てる3つの習慣</strong></p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p><strong>1. 毎日一つ、新しいことを試す</strong><br>私は毎朝の通勤ルートを意識的に変えることから始めました。最初は不安でしたが、新しい発見があることに気づき、変化を楽しめるようになりました。</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p><strong>2. 失敗を恐れない環境作り</strong><br>信頼できる人に自分の挑戦を話し、応援してもらえる関係性を築くことが重要です。妻が「失敗しても一緒に乗り越えよう」と言ってくれたことで、転職への一歩を踏み出せました。</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p><strong>3. 成功体験の積み重ね</strong><br>私は「今日できたこと日記」を実践しています。毎日寝る前に、その日達成できたことを3つ書き出すのです。小さなことでも、すべてが貴重な成功体験になります。</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":2} -->
<h2 class="wp-block-heading">第6章：働き方設計 - 人生を豊かにする仕事との向き合い方</h2>
<!-- /wp:heading -->

<!-- wp:image {"id":3273,"sizeSlug":"full","linkDestination":"none"} -->
<figure class="wp-block-image size-full"><img src="https://www.ht-sw.tech/wp-content/uploads/2025/07/20250714_112438_thumbnail_unknown_chapter6.jpg" alt="第6章 サムネイル画像" class="wp-image-3273"/></figure>
<!-- /wp:image -->

<!-- wp:paragraph -->
<p>働き方について考える時、多くの人が「効率」や「成果」ばかりに目を向けがちです。しかし、本当に大切なのは、自分らしい働き方を見つけて、仕事を通じて人生を豊かにすることです。</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":3} -->
<h3 class="wp-block-heading">家族をきっかけに見直した働き方</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>私が働き方について真剣に考え始めたのは、長男が生まれた時でした。それまでは仕事最優先で、夜遅くまで残業することが当たり前でした。妻から「子どもの成長は一度きり。家族との時間も大切にしてほしい」と言われた時、ハッとしたのです。</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>当時の課題：</p>
<!-- /wp:paragraph -->

<!-- wp:list -->
<ul>
<li>毎日深夜まで残業</li>
<li>家族との時間が取れない</li>
<li>疲れがたまって健康面も心配</li>
</ul>
<!-- /wp:list -->

<!-- wp:paragraph -->
<p>これらを解決するため、働き方の「設計図」を作ることにしました。</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":3} -->
<h3 class="wp-block-heading">価値観を明確にする重要性</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>働き方設計の第一歩は、自分の価値観を明確にすることです。私が実践した方法をご紹介します。</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p><strong>🎯 価値観発見の3つの質問</strong></p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p><strong>1. 人生の最期を想像する</strong><br>今日が人生最後の日だとしたら、何を後悔するでしょうか。私の場合、「子どもともっと時間を過ごせばよかった」という思いが浮かびました。</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p><strong>2. 理想の一日を描く</strong><br>私の理想：朝は家族と朝食、午前は集中して仕事、夕方には家族と夕食、夜は子どもと遊ぶ時間。</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p><strong>3. 大切な人からの言葉を想像する</strong><br>「仕事も家庭も大切にする人」と言われたいと気づきました。</p>
<!-- /wp:paragraph -->

'''
        
        # 破綻部分を正しいコンテンツで置換
        fixed_content = content[:broken_start] + fixed_chapters + content[broken_end:]
        
        print(f'修正後文字数: {len(fixed_content)}')
        
        # WordPress更新実行
        result = client.update_post(
            post_id=2127,
            content=fixed_content,
            backup=True
        )
        print(f'✅ 第5-6章修正完了: {result.get("post_id", "Unknown")}')
        
        return True
        
    else:
        print('❌ 破綻範囲が特定できませんでした')
        print(f'broken_start: {broken_start}')
        print(f'broken_end: {broken_end}')
        return False

if __name__ == "__main__":
    fix_chapter_structure()