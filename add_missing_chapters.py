#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WordPress記事2127に不足している第5章・第6章・まとめを追加
"""

import sys
sys.path.append('/mnt/c/home/hiroshi/blog_generator/scripts')
from wordpress_update_client import WordPressUpdateClient

def add_missing_chapters():
    """第5章・第6章・まとめを確実に追加"""
    
    # 現在の記事を取得
    client = WordPressUpdateClient(integration_mode=True)
    current_post = client.get_post(2127)
    current_content = current_post.get('content', '')
    
    print(f'現在のコンテンツ文字数: {len(current_content)}')
    
    # 第4章の内容を探して、その後に追加
    # より確実な検索パターンを使用
    fourth_chapter_patterns = [
        '「新しいことを学ぶのって楽しい」と心から思えるようになったんです。</p>',
        '3ヶ月後には、新しいシステムを完全にマスターし',
        '第4章：適応力'
    ]
    
    insertion_point = -1
    for pattern in fourth_chapter_patterns:
        pos = current_content.find(pattern)
        if pos != -1:
            # パターンの終わりを探す
            if pattern.endswith('</p>'):
                insertion_point = pos + len(pattern)
            else:
                # </p>まで探す
                next_p_end = current_content.find('</p>', pos)
                if next_p_end != -1:
                    insertion_point = next_p_end + 4  # '</p>'の長さ
            break
    
    if insertion_point != -1:
        print(f'挿入ポイント発見: 位置 {insertion_point}')
        
        # 現在のコンテンツを分割
        before_content = current_content[:insertion_point]
        after_content = current_content[insertion_point:]
        
        # 追加する第5章・第6章・まとめのコンテンツ
        missing_chapters = '''
<!-- /wp:paragraph -->

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

<!-- wp:heading {"level":2} -->
<h2 class="wp-block-heading">まとめ</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>AI時代を生きる私たちにとって、技術的なスキルも確かに重要です。でも、それ以上に大切なのは、人間らしい温かさや思いやり、そして成長し続ける心なのではないでしょうか。</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>この記事でお伝えした6つのスキル—共感力、感情管理、コミュニケーション力、適応力、挑戦する勇気、そして自分らしい働き方の設計—は、すべて人間だからこそ身につけることができる特別な能力です。</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p><strong>大切なのは、完璧を目指すことではありません。毎日少しずつ、自分なりのペースで成長していくことです。</strong> 昨日の自分よりも、ほんの少しでも優しくなれたら、ほんの少しでも勇気を出せたら、それで十分なんです。</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>AI時代だからこそ、私たち人間の価値は高まっています。機械にはできない、心と心のつながりを大切にしながら、一緒に成長していきましょう。</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>あなたの人生が、より豊かで温かいものになることを心から願っています。</p>
<!-- /wp:paragraph -->'''
        
        # 完全なコンテンツを構築（重複を避けるため、after_contentはクリア）
        complete_content = before_content + missing_chapters
        
        print(f'完全なコンテンツ文字数: {len(complete_content)}')
        
        # WordPress更新実行
        result = client.update_post(
            post_id=2127,
            content=complete_content,
            backup=True
        )
        
        print(f'✅ 第5章・第6章・まとめを追加更新完了')
        print(f'   投稿ID: {result.get("post_id", "Unknown")}')
        print(f'   更新時刻: {result.get("modified_time", "Unknown")}')
        
        return True
        
    else:
        print(f'❌ 第4章の終わりが見つかりませんでした')
        print(f'現在のコンテンツの末尾300文字:')
        print(current_content[-300:])
        return False

if __name__ == "__main__":
    add_missing_chapters()