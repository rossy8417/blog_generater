<?php
/*
Plugin Name: Blog Generator Plugin
Description: WordPress plugin to import blog articles from outputs folder with chapter-by-chapter processing and advanced update functionality
Version: 2.1
Author: Your Name
*/

// セキュリティ対策：直接アクセスを防ぐ
if (!defined('ABSPATH')) {
    exit;
}

class Blog_Generator_Plugin {
    private static $instance = null;

    // シングルトンパターンでインスタンスを取得
    public static function get_instance() {
        if (null === self::$instance) {
            self::$instance = new self();
        }
        return self::$instance;
    }

    // コンストラクタ：フックを追加
    private function __construct() {
        add_action('admin_menu', array($this, 'add_plugin_page'));
        add_action('rest_api_init', array($this, 'register_rest_routes'));
        
        // デバッグ用：ログ出力を有効化
        if (!defined('WP_DEBUG') || !WP_DEBUG) {
            ini_set('log_errors', 1);
            ini_set('error_log', WP_CONTENT_DIR . '/debug.log');
        }
    }

    // プラグインの設定ページを追加
    public function add_plugin_page() {
        add_menu_page(
            'Blog Generator',
            'Blog Generator',
            'manage_options',
            'blog-generator',
            array($this, 'create_admin_page'),
            'dashicons-edit-large',
            99
        );
    }

    // プラグインの設定ページを作成
    public function create_admin_page() {
        // 設定の保存処理
        if (isset($_POST['submit']) && wp_verify_nonce($_POST['blog_generator_nonce'], 'blog_generator_settings')) {
            $this->save_settings();
            echo '<div class="notice notice-success is-dismissible"><p>設定を保存しました。</p></div>';
        }
        
        // APIキー生成処理
        if (isset($_POST['generate_api_key']) && wp_verify_nonce($_POST['blog_generator_nonce'], 'blog_generator_settings')) {
            $this->generate_new_api_key();
            echo '<div class="notice notice-success is-dismissible"><p>新しいAPIキーを生成しました。</p></div>';
        }
        
        $plugin_api_key = get_option('blog_generator_plugin_api_key', '');
        $site_url = get_site_url();
        $rest_endpoint = $site_url . '/wp-json/blog-generator/v1';
        
        ?>
        <div class="wrap">
            <h1>ブログジェネレーター</h1>
            
            <div class="card">
                <h2>API接続設定</h2>
                <p>Claude Codeからこのプラグインに接続するための設定情報です。</p>
                
                <form method="post" action="">
                    <?php wp_nonce_field('blog_generator_settings', 'blog_generator_nonce'); ?>
                    
                    <div class="api-settings-grid">
                        <div class="api-key-section">
                            <h3>プラグインAPIキー</h3>
                            <div class="input-group">
                                <input type="text" id="plugin_api_key" 
                                       value="<?php echo esc_attr($plugin_api_key); ?>" 
                                       class="api-key-input" readonly 
                                       placeholder="APIキーが表示されます">
                                <div class="button-group">
                                    <button type="submit" name="generate_api_key" class="button button-primary">
                                        <?php echo empty($plugin_api_key) ? 'APIキーを生成' : '新しいキーを生成'; ?>
                                    </button>
                                    <button type="button" id="copy-api-key" class="button button-secondary">Copy</button>
                                </div>
                            </div>
                            <p class="description">Claude Codeの.envファイルにWORDPRESS_API_KEYとして設定</p>
                        </div>
                        
                        <div class="endpoint-section">
                            <h3>REST APIエンドポイント</h3>
                            <div class="input-group">
                                <input type="url" id="rest_endpoint" 
                                       value="<?php echo esc_attr($rest_endpoint); ?>" 
                                       class="endpoint-input" readonly>
                                <div class="button-group">
                                    <button type="button" id="copy-endpoint" class="button button-secondary">Copy</button>
                                </div>
                            </div>
                            <p class="description">Claude Codeの.envファイルにWORDPRESS_ENDPOINTとして設定</p>
                        </div>
                    </div>
                </form>
            </div>
            
            <div class="card instructions-card">
                <h2>🚀 Claude Code連携手順</h2>
                <div class="steps-container">
                    <div class="step">
                        <div class="step-number">1</div>
                        <div class="step-content">
                            <h4>APIキーを生成・コピー</h4>
                            <p>上記の「APIキーを生成」ボタンをクリックし、生成されたAPIキーをコピー</p>
                        </div>
                    </div>
                    
                    <div class="step">
                        <div class="step-number">2</div>
                        <div class="step-content">
                            <h4>.envファイルに追加</h4>
                            <div class="code-block">
                                <code>WORDPRESS_API_KEY=<span class="placeholder">コピーしたAPIキー</span></code><br>
                                <code>WORDPRESS_ENDPOINT=<?php echo esc_attr($rest_endpoint); ?></code>
                            </div>
                        </div>
                    </div>
                    
                    <div class="step">
                        <div class="step-number">3</div>
                        <div class="step-content">
                            <h4>接続テスト実行</h4>
                            <div class="code-block">
                                <code>python wordpress_client.py</code>
                            </div>
                        </div>
                    </div>
                    
                    <div class="step">
                        <div class="step-number">4</div>
                        <div class="step-content">
                            <h4>ブログ記事生成</h4>
                            <p>Claude Codeで「ブログ投稿」コマンドを実行</p>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="card usage-card">
                <h2>📈 API使用状況</h2>
                <div class="usage-stats">
                    <div class="stat-item">
                        <div class="stat-number" id="today-count">0</div>
                        <div class="stat-label">今日の生成数</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number" id="total-count">0</div>
                        <div class="stat-label">総生成数</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number connection-status" id="connection-status">•</div>
                        <div class="stat-label">接続状態</div>
                    </div>
                </div>
            </div>

            <style>
                .card {
                    background: #fff;
                    padding: 20px;
                    margin: 20px 0;
                    border: 1px solid #ccd0d4;
                    box-shadow: 0 1px 1px rgba(0,0,0,.04);
                    border-radius: 8px;
                }
                
                .api-settings-grid {
                    display: grid;
                    gap: 30px;
                    margin-bottom: 20px;
                }
                
                .api-key-section, .endpoint-section {
                    border: 1px solid #e0e0e0;
                    border-radius: 6px;
                    padding: 20px;
                    background: #fafafa;
                }
                
                .api-key-section h3, .endpoint-section h3 {
                    margin: 0 0 15px 0;
                    color: #1d2327;
                    font-size: 16px;
                }
                
                .input-group {
                    display: flex;
                    gap: 10px;
                    align-items: flex-start;
                    margin-bottom: 10px;
                }
                
                .api-key-input, .endpoint-input {
                    flex: 1;
                    min-width: 0;
                    padding: 8px 12px;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    background: #fff;
                    font-family: monospace;
                    font-size: 13px;
                }
                
                .button-group {
                    display: flex;
                    gap: 8px;
                    flex-shrink: 0;
                }
                
                .instructions-card .steps-container {
                    display: grid;
                    gap: 20px;
                }
                
                .step {
                    display: flex;
                    gap: 15px;
                    align-items: flex-start;
                }
                
                .step-number {
                    width: 30px;
                    height: 30px;
                    background: #0073aa;
                    color: white;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-weight: bold;
                    flex-shrink: 0;
                }
                
                .step-content h4 {
                    margin: 0 0 8px 0;
                    color: #1d2327;
                }
                
                .step-content p {
                    margin: 0;
                    color: #646970;
                }
                
                .code-block {
                    background: #f6f7f7;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    padding: 12px;
                    margin: 8px 0;
                    font-family: monospace;
                    font-size: 13px;
                    overflow-x: auto;
                }
                
                .code-block code {
                    background: none;
                    padding: 0;
                }
                
                .placeholder {
                    color: #0073aa;
                    font-style: italic;
                }
                
                .usage-stats {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                    gap: 20px;
                    text-align: center;
                }
                
                .stat-item {
                    padding: 15px;
                    background: #f9f9f9;
                    border-radius: 6px;
                    border: 1px solid #e0e0e0;
                }
                
                .stat-number {
                    font-size: 24px;
                    font-weight: bold;
                    color: #0073aa;
                    margin-bottom: 5px;
                }
                
                .stat-label {
                    font-size: 12px;
                    color: #646970;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }
                
                .connection-status {
                    color: #46b450;
                }
                
                @media (max-width: 768px) {
                    .input-group {
                        flex-direction: column;
                        align-items: stretch;
                    }
                    
                    .button-group {
                        justify-content: flex-start;
                    }
                }
            </style>

            <script>
                jQuery(document).ready(function($) {
                    // APIキーコピー機能
                    $('#copy-api-key').on('click', function() {
                        copyToClipboard($('#plugin_api_key').val());
                    });
                    
                    $('#copy-endpoint').on('click', function() {
                        copyToClipboard($('#rest_endpoint').val());
                    });
                    
                    function copyToClipboard(text) {
                        navigator.clipboard.writeText(text).then(function() {
                            alert('コピーしました！');
                        });
                    }
                    
                    // API使用状況更新
                    updateApiUsage();
                    
                    function updateApiUsage() {
                        $.get('/wp-json/blog-generator/v1/usage', function(data) {
                            $('#today-count').text(data.today_count || 0);
                            $('#total-count').text(data.total_count || 0);
                        });
                    }

                    // 記事構成生成
                    $('#generate-outline').on('click', function() {
                        let keywords = $('#blog-keywords').val().trim();
                        if (!keywords) {
                            alert('キーワードを入力してください。');
                            return;
                        }
                        
                        if (generationInProgress) {
                            alert('現在生成中です。しばらくお待ちください。');
                            return;
                        }
                        
                        startGeneration('outline', keywords);
                    });
                    
                    // 完全自動生成
                    $('#generate-full-article').on('click', function() {
                        let keywords = $('#blog-keywords').val().trim();
                        if (!keywords) {
                            alert('キーワードを入力してください。');
                            return;
                        }
                        
                        if (generationInProgress) {
                            alert('現在生成中です。しばらくお待ちください。');
                            return;
                        }
                        
                        startGeneration('full', keywords);
                    });

                    // 生成開始処理
                    function startGeneration(mode, keywords) {
                        generationInProgress = true;
                        $('#generation-progress').show();
                        $('#progress-log').empty();
                        
                        addProgressLog('生成を開始します... モード: ' + mode + ', キーワード: ' + keywords, 'processing');
                        
                        // モードによって処理を分岐
                        if (mode === 'outline') {
                            generateOutlineOnly(keywords);
                        } else if (mode === 'full') {
                            generateFullArticle(keywords);
                        }
                    }
                    
                    // 記事構成のみ生成
                    function generateOutlineOnly(keywords) {
                        addProgressLog('検索意図を分析中...', 'processing');
                        
                        $.post(ajaxurl, {
                            action: 'generate_blog_content',
                            step: 'outline_only',
                            keywords: keywords,
                            nonce: '<?php echo wp_create_nonce('blog_generator_nonce'); ?>'
                        }, function(response) {
                            if (response.success) {
                                addProgressLog('記事構成が生成されました！');
                                showGenerationResult(response.data);
                            } else {
                                addProgressLog('エラー: ' + response.data, 'error');
                            }
                            generationInProgress = false;
                        }).fail(function() {
                            addProgressLog('サーバーエラーが発生しました。', 'error');
                            generationInProgress = false;
                        });
                    }
                    
                    // 完全記事生成
                    function generateFullArticle(keywords) {
                        addProgressLog('完全自動生成を開始します...', 'processing');
                        
                        $.post(ajaxurl, {
                            action: 'generate_blog_content',
                            step: 'full_article',
                            keywords: keywords,
                            nonce: '<?php echo wp_create_nonce('blog_generator_nonce'); ?>'
                        }, function(response) {
                            if (response.success) {
                                addProgressLog('記事が完成しました！');
                                showGenerationResult(response.data);
                            } else {
                                addProgressLog('エラー: ' + response.data, 'error');
                            }
                            generationInProgress = false;
                        }).fail(function() {
                            addProgressLog('サーバーエラーが発生しました。', 'error');
                            generationInProgress = false;
                        });
                    }

                    // インポート開始
                    $('#start-import').on('click', function() {
                        $('#import-progress').show();
                        $('#progress-log').empty();
                        processStep(0);
                    });

                    // ステップ別処理
                    function processStep(step) {
                        if (step === 0) {
                            // Step 0: リード文で新規記事作成
                            debugLog('Step 0: Creating initial post with lead...');
                            createInitialPost();
                        } else if (step <= chapterFiles.length) {
                            // Step 1-N: 各章を追加
                            debugLog('Step ' + step + ': Adding chapter ' + step);
                            addChapter(step - 1, function() {
                                processStep(step + 1);
                            });
                        } else {
                            // Step Final: まとめ文を追加
                            debugLog('Final Step: Adding summary...');
                            addSummary();
                        }
                    }

                    // 初期化
                    // APIキーが設定されているかチェック
                    checkApiSettings();
                    
                    function checkApiSettings() {
                        let geminiKey = '<?php echo esc_js(get_option('blog_generator_gemini_api_key', '')); ?>';
                        if (!geminiKey) {
                            addProgressLog('‼️ APIキーが設定されていません。上の「API設定」でGemini APIキーを設定してください。', 'error');
                        }
                    }

                    // 章を追加
                    function addChapter(chapterIndex, callback) {
                        let chapter = chapterFiles[chapterIndex];
                        addProgressLog('Adding chapter ' + (chapterIndex + 1) + ': ' + chapter.title, 'processing');
                        
                        $.post(ajaxurl, {
                            action: 'process_chapter',
                            step: 'chapter',
                            post_id: currentPostId,
                            chapter_index: chapterIndex,
                            chapter_file: chapter,
                            outline_data: outlineData,
                            nonce: '<?php echo wp_create_nonce('blog_generator_nonce'); ?>'
                        }, function(response) {
                            debugLog('Chapter ' + (chapterIndex + 1) + ' response:', response);
                            if (response.success) {
                                addProgressLog('✓ Chapter ' + (chapterIndex + 1) + ' added successfully');
                                callback();
                            } else {
                                addProgressLog('✗ Failed to add chapter ' + (chapterIndex + 1) + ': ' + response.data, 'error');
                            }
                        });
                    }

                    // まとめ文を追加
                    function addSummary() {
                        addProgressLog('Adding summary...', 'processing');
                        
                        $.post(ajaxurl, {
                            action: 'process_chapter',
                            step: 'summary',
                            post_id: currentPostId,
                            outline_data: outlineData,
                            nonce: '<?php echo wp_create_nonce('blog_generator_nonce'); ?>'
                        }, function(response) {
                            debugLog('Summary response:', response);
                            if (response.success) {
                                addProgressLog('✓ Summary added successfully');
                                showFinalResult();
                            } else {
                                addProgressLog('✗ Failed to add summary: ' + response.data, 'error');
                            }
                        });
                    }

                    // 最終結果表示
                    function showFinalResult() {
                        $('#final-result').html(
                            '<div class="card" style="background: #d4edda; border-color: #c3e6cb;">' +
                            '<h3>Import Completed!</h3>' +
                            '<p><strong>Post ID:</strong> ' + currentPostId + '</p>' +
                            '<p><a href="<?php echo admin_url('post.php?action=edit&post='); ?>' + currentPostId + '" class="button button-primary">Edit Post</a></p>' +
                            '</div>'
                        );
                    }

                    // プログレスログに追加
                    function addProgressLog(message, type = 'success') {
                        let className = 'progress-item';
                        if (type === 'error') className += ' error';
                        if (type === 'processing') className += ' processing';
                        
                        $('#progress-log').append('<div class="' + className + '">' + message + '</div>');
                        $('#progress-log').scrollTop($('#progress-log')[0].scrollHeight);
                    }

                    // 生成結果表示
                    function showGenerationResult(data) {
                        let resultHtml = '<div class="card" style="background: #d4edda; border-color: #c3e6cb;">';
                        resultHtml += '<h3>生成完了！</h3>';
                        
                        if (data.post_id) {
                            resultHtml += '<p><strong>投稿ID:</strong> ' + data.post_id + '</p>';
                            resultHtml += '<p><a href="<?php echo admin_url('post.php?action=edit&post='); ?>' + data.post_id + '" class="button button-primary">記事を編集</a></p>';
                        }
                        
                        if (data.files_generated) {
                            resultHtml += '<p><strong>生成ファイル数:</strong> ' + data.files_generated + '</p>';
                        }
                        
                        resultHtml += '</div>';
                        $('#final-result').html(resultHtml);
                    }
                });
            </script>
        </div>
        <?php
    }

    // REST APIルート登録
    public function register_rest_routes() {
        register_rest_route('blog-generator/v1', '/create-post', array(
            'methods' => 'POST',
            'callback' => array($this, 'rest_create_post'),
            'permission_callback' => array($this, 'check_api_permission')
        ));
        
        register_rest_route('blog-generator/v1', '/usage', array(
            'methods' => 'GET',
            'callback' => array($this, 'rest_get_usage'),
            'permission_callback' => array($this, 'check_api_permission')
        ));
        
        register_rest_route('blog-generator/v1', '/upload-image', array(
            'methods' => 'POST',
            'callback' => array($this, 'rest_upload_image'),
            'permission_callback' => array($this, 'check_api_permission')
        ));
        
        // 記事更新機能のエンドポイント追加（PUTとPOST両対応）
        register_rest_route('blog-generator/v1', '/update-post/(?P<id>\d+)', array(
            'methods' => array('PUT', 'POST'),
            'callback' => array($this, 'rest_update_post'),
            'permission_callback' => array($this, 'check_api_permission'),
            'args' => array(
                'id' => array(
                    'validate_callback' => function($param, $request, $key) {
                        return is_numeric($param);
                    }
                )
            )
        ));
        
        register_rest_route('blog-generator/v1', '/get-post/(?P<id>\d+)', array(
            'methods' => 'GET',
            'callback' => array($this, 'rest_get_post'),
            'permission_callback' => array($this, 'check_api_permission'),
            'args' => array(
                'id' => array(
                    'validate_callback' => function($param, $request, $key) {
                        return is_numeric($param);
                    }
                )
            )
        ));
        
        register_rest_route('blog-generator/v1', '/backup-post/(?P<id>\d+)', array(
            'methods' => 'POST',
            'callback' => array($this, 'rest_backup_post'),
            'permission_callback' => array($this, 'check_api_permission'),
            'args' => array(
                'id' => array(
                    'validate_callback' => function($param, $request, $key) {
                        return is_numeric($param);
                    }
                )
            )
        ));
        
        register_rest_route('blog-generator/v1', '/restore-post/(?P<id>\d+)', array(
            'methods' => 'POST',
            'callback' => array($this, 'rest_restore_post'),
            'permission_callback' => array($this, 'check_api_permission'),
            'args' => array(
                'id' => array(
                    'validate_callback' => function($param, $request, $key) {
                        return is_numeric($param);
                    }
                )
            )
        ));
        
        register_rest_route('blog-generator/v1', '/search-posts', array(
            'methods' => 'GET',
            'callback' => array($this, 'rest_search_posts'),
            'permission_callback' => array($this, 'check_api_permission')
        ));
        
        register_rest_route('blog-generator/v1', '/analytics/(?P<id>\d+)', array(
            'methods' => 'GET',
            'callback' => array($this, 'rest_get_analytics'),
            'permission_callback' => array($this, 'check_api_permission'),
            'args' => array(
                'id' => array(
                    'validate_callback' => function($param, $request, $key) {
                        return is_numeric($param);
                    }
                )
            )
        ));
    }
    
    // APIアクセス権限チェック
    public function check_api_permission($request) {
        $api_key = $request->get_header('X-API-Key');
        if (!$api_key) {
            $api_key = $request->get_param('api_key');
        }
        
        $stored_api_key = get_option('blog_generator_plugin_api_key', '');
        
        if (empty($stored_api_key) || $api_key !== $stored_api_key) {
            return new WP_Error('unauthorized', 'Invalid API key', array('status' => 401));
        }
        
        return true;
    }
    
    // APIキー生成
    private function generate_new_api_key() {
        $api_key = 'bgen_' . wp_generate_password(32, false);
        update_option('blog_generator_plugin_api_key', $api_key);
        $this->debug_log('New API key generated');
    }
    
    // 設定保存処理
    private function save_settings() {
        if (!current_user_can('manage_options')) {
            return;
        }
        
        $this->debug_log('Settings saved successfully');
    }

    // REST API: 記事作成エンドポイント
    public function rest_create_post(WP_REST_Request $request) {
        try {
            $title = sanitize_text_field($request->get_param('title'));
            $content = wp_kses_post($request->get_param('content'));
            $excerpt = sanitize_text_field($request->get_param('excerpt'));
            $status = sanitize_text_field($request->get_param('status')) ?: 'draft';
            $meta_description = sanitize_text_field($request->get_param('meta_description'));
            $featured_image_id = intval($request->get_param('featured_image_id'));
            
            $this->debug_log('Creating post via REST API:', array(
                'title' => $title,
                'status' => $status,
                'content_length' => strlen($content)
            ));
            
            // 記事作成
            $post_data = array(
                'post_title' => $title,
                'post_content' => $content,
                'post_excerpt' => $excerpt,
                'post_status' => $status,
                'post_author' => 1,
                'post_name' => sanitize_title($title)
            );

            $post_id = wp_insert_post($post_data);
            
            if (is_wp_error($post_id)) {
                throw new Exception('記事の作成に失敗しました: ' . $post_id->get_error_message());
            }

            // メタディスクリプション設定
            if ($meta_description) {
                update_post_meta($post_id, '_meta_description', $meta_description);
            }
            
            // アイキャッチ画像設定
            if ($featured_image_id && $featured_image_id > 0) {
                $thumbnail_result = set_post_thumbnail($post_id, $featured_image_id);
                $this->debug_log('Featured image set result:', array(
                    'post_id' => $post_id,
                    'featured_image_id' => $featured_image_id,
                    'success' => $thumbnail_result
                ));
            }
            
            // 使用状況更新
            $this->update_usage_stats();
            
            return rest_ensure_response(array(
                'success' => true,
                'post_id' => $post_id,
                'edit_url' => admin_url('post.php?action=edit&post=' . $post_id),
                'preview_url' => get_preview_post_link($post_id)
            ));
            
        } catch (Exception $e) {
            $this->debug_log('Error in rest_create_post:', $e->getMessage());
            return new WP_Error('creation_failed', $e->getMessage(), array('status' => 500));
        }
    }
    
    // REST API: 使用状況取得
    public function rest_get_usage(WP_REST_Request $request) {
        $today_count = get_option('blog_generator_today_count', 0);
        $total_count = get_option('blog_generator_total_count', 0);
        $last_used = get_option('blog_generator_last_used', '');
        
        return rest_ensure_response(array(
            'today_count' => $today_count,
            'total_count' => $total_count,
            'last_used' => $last_used
        ));
    }
    
    // 使用状況更新
    private function update_usage_stats() {
        $today = date('Y-m-d');
        $last_used_date = get_option('blog_generator_last_used_date', '');
        
        if ($last_used_date !== $today) {
            // 日付が変わったら今日のカウントをリセット
            update_option('blog_generator_today_count', 1);
            update_option('blog_generator_last_used_date', $today);
        } else {
            // 今日のカウントをインクリメント
            $today_count = get_option('blog_generator_today_count', 0);
            update_option('blog_generator_today_count', $today_count + 1);
        }
        
        // 総カウントをインクリメント
        $total_count = get_option('blog_generator_total_count', 0);
        update_option('blog_generator_total_count', $total_count + 1);
        update_option('blog_generator_last_used', current_time('mysql'));
    }
    
    // REST API: 画像アップロードエンドポイント
    public function rest_upload_image(WP_REST_Request $request) {
        try {
            if (empty($_FILES['file'])) {
                return new WP_Error('no_file', 'ファイルがアップロードされていません', array('status' => 400));
            }
            
            $file = $_FILES['file'];
            $alt_text = sanitize_text_field($request->get_param('alt_text')) ?: '';
            
            $this->debug_log('Uploading image via REST API:', array(
                'filename' => $file['name'],
                'size' => $file['size'],
                'alt_text' => $alt_text
            ));
            
            // WordPress標準のファイルアップロード処理
            require_once(ABSPATH . 'wp-admin/includes/file.php');
            require_once(ABSPATH . 'wp-admin/includes/media.php');
            require_once(ABSPATH . 'wp-admin/includes/image.php');
            
            $attachment_id = media_handle_upload('file', 0, array(
                'post_title' => $alt_text ?: pathinfo($file['name'], PATHINFO_FILENAME),
                'post_content' => '',
                'post_excerpt' => $alt_text
            ));
            
            if (is_wp_error($attachment_id)) {
                throw new Exception('画像のアップロードに失敗しました: ' . $attachment_id->get_error_message());
            }
            
            // alt属性を設定
            if ($alt_text) {
                update_post_meta($attachment_id, '_wp_attachment_image_alt', $alt_text);
            }
            
            $attachment_url = wp_get_attachment_url($attachment_id);
            
            $this->debug_log('Image uploaded successfully:', array(
                'attachment_id' => $attachment_id,
                'url' => $attachment_url
            ));
            
            return rest_ensure_response(array(
                'success' => true,
                'attachment_id' => $attachment_id,
                'url' => $attachment_url,
                'alt_text' => $alt_text
            ));
            
        } catch (Exception $e) {
            $this->debug_log('Error in rest_upload_image:', $e->getMessage());
            return new WP_Error('upload_failed', $e->getMessage(), array('status' => 500));
        }
    }

    // アウトライン生成（APIコール）
    private function generate_outline_via_api($keywords) {
        $this->debug_log('Generating outline for keywords:', $keywords);
        
        // TODO: 実際のGemini APIコールを実装
        // 現在は仮実装
        $outline_data = array(
            'title' => $keywords . 'に関する完全ガイド',
            'meta_description' => $keywords . 'について専門家が解説する包括的ガイド',
            'slug' => sanitize_title($keywords . '-complete-guide'),
            'chapters' => array(
                array('title' => $keywords . 'とは？基本概念の理解', 'content' => ''),
                array('title' => $keywords . 'の実践的活用方法', 'content' => ''),
                array('title' => $keywords . 'の将来展望とまとめ', 'content' => '')
            )
        );
        
        // ファイル保存
        $timestamp = date('Ymd_His');
        $outline_file = dirname(__FILE__) . '/outputs/' . $timestamp . '_outline_generated.md';
        
        $outline_content = "# " . $outline_data['title'] . "\n\n";
        $outline_content .= "meta_description: " . $outline_data['meta_description'] . "\n\n";
        
        foreach ($outline_data['chapters'] as $i => $chapter) {
            $outline_content .= "## " . ($i + 1) . ". " . $chapter['title'] . "\n";
        }
        
        file_put_contents($outline_file, $outline_content);
        
        return array(
            'outline_file' => $outline_file,
            'outline_data' => $outline_data,
            'files_generated' => 1
        );
    }
    
    // 完全記事生成（APIコール）
    private function generate_full_article_via_api($keywords) {
        $this->debug_log('Generating full article for keywords:', $keywords);
        
        // アウトライン生成
        $outline_result = $this->generate_outline_via_api($keywords);
        $outline_data = $outline_result['outline_data'];
        
        // WordPress記事作成
        $post_data = array(
            'post_title' => $outline_data['title'],
            'post_content' => $this->generate_article_content($outline_data),
            'post_excerpt' => $outline_data['meta_description'],
            'post_status' => 'draft',
            'post_author' => get_current_user_id(),
            'post_name' => $outline_data['slug']
        );

        $post_id = wp_insert_post($post_data);
        
        if (is_wp_error($post_id)) {
            throw new Exception('記事の作成に失敗しました: ' . $post_id->get_error_message());
        }

        // メタディスクリプション設定
        update_post_meta($post_id, '_meta_description', $outline_data['meta_description']);
        
        return array(
            'post_id' => $post_id,
            'outline_data' => $outline_data,
            'files_generated' => count($outline_data['chapters']) + 1
        );
    }
    
    // 記事コンテンツ生成
    private function generate_article_content($outline_data) {
        $content = "<!-- wp:paragraph -->\n";
        $content .= "<p>" . $outline_data['title'] . "について詳しく解説します。</p>\n";
        $content .= "<!-- /wp:paragraph -->\n\n";
        
        foreach ($outline_data['chapters'] as $i => $chapter) {
            $content .= "<!-- wp:heading {\"level\":2} -->\n";
            $content .= "<h2 class=\"wp-block-heading\">" . $chapter['title'] . "</h2>\n";
            $content .= "<!-- /wp:heading -->\n\n";
            
            $content .= "<!-- wp:paragraph -->\n";
            $content .= "<p>" . $chapter['title'] . "についての詳細な内容をここに記載します。</p>\n";
            $content .= "<!-- /wp:paragraph -->\n\n";
        }
        
        return $content;
    }

    // デバッグログ出力
    private function debug_log($message, $data = null) {
        $log_message = '[Blog Generator] ' . $message;
        if ($data !== null) {
            $log_message .= ' | Data: ' . print_r($data, true);
        }
        error_log($log_message);
    }

    // アウトラインファイル解析
    private function parse_outline_file($file_path) {
        if (!file_exists($file_path)) {
            $this->debug_log('Outline file not found:', $file_path);
            return false;
        }

        $content = file_get_contents($file_path);
        $lines = explode("\n", $content);
        
        $title = '';
        $meta_description = '';
        
        foreach ($lines as $line) {
            if (preg_match('/^# (.+)/', $line, $matches)) {
                $title = trim($matches[1]);
            } elseif (preg_match('/meta_description:\s*(.+)/', $line, $matches)) {
                $meta_description = trim($matches[1], '"');
            }
        }

        return array(
            'title' => $title,
            'meta_description' => $meta_description,
            'file_path' => $file_path
        );
    }

    // 章ファイル検索
    private function find_chapter_files($outline_path) {
        $path_info = pathinfo($outline_path);
        $base_pattern = str_replace('_outline_', '_article_', $path_info['dirname'] . '/' . $path_info['filename']);
        
        $chapter_files = array();
        $chapter_pattern = $base_pattern . '_chapter*.md';
        
        $files = glob($chapter_pattern);
        sort($files);
        
        foreach ($files as $file) {
            if (preg_match('/_chapter(\d+)\.md$/', $file, $matches)) {
                $chapter_num = intval($matches[1]);
                $chapter_files[] = array(
                    'number' => $chapter_num,
                    'path' => $file,
                    'title' => $this->extract_chapter_title($file)
                );
            }
        }
        
        return $chapter_files;
    }

    // 章タイトル抽出
    private function extract_chapter_title($file_path) {
        if (!file_exists($file_path)) {
            return 'Unknown Chapter';
        }
        
        $content = file_get_contents($file_path);
        $lines = explode("\n", $content);
        
        foreach ($lines as $line) {
            if (preg_match('/^## (.+)/', $line, $matches)) {
                return trim($matches[1]);
            }
        }
        
        return 'Chapter ' . basename($file_path);
    }

    // 初回投稿作成（リード文 + メタ情報）
    private function create_initial_post($outline_data) {
        $this->debug_log('Creating initial post with outline data:', $outline_data);
        
        // リード文ファイル検索
        $lead_file = $this->find_lead_file($outline_data['file_path']);
        $lead_content = '';
        
        if ($lead_file && file_exists($lead_file)) {
            $lead_content = file_get_contents($lead_file);
            $this->debug_log('Lead file found and loaded:', $lead_file);
        } else {
            $this->debug_log('Lead file not found, using placeholder');
            $lead_content = '<!-- wp:paragraph --><p>リード文を準備中...</p><!-- /wp:paragraph -->';
        }

        // 記事タイトルの英語化・スラッグ生成
        $slug = $this->generate_slug($outline_data['title']);
        
        $post_data = array(
            'post_title' => $outline_data['title'],
            'post_content' => $lead_content,
            'post_excerpt' => $outline_data['meta_description'],
            'post_status' => 'draft',
            'post_author' => get_current_user_id(),
            'post_name' => $slug
        );

        $post_id = wp_insert_post($post_data);
        
        if (is_wp_error($post_id)) {
            throw new Exception('Failed to create post: ' . $post_id->get_error_message());
        }

        // メタディスクリプション設定
        update_post_meta($post_id, '_meta_description', $outline_data['meta_description']);

        // アイキャッチ画像設定
        $eyecatch_result = $this->set_eyecatch_image($post_id, $outline_data);
        
        $this->debug_log('Initial post created successfully:', array(
            'post_id' => $post_id,
            'slug' => $slug,
            'eyecatch_result' => $eyecatch_result
        ));

        return array(
            'post_id' => $post_id,
            'slug' => $slug,
            'eyecatch_set' => $eyecatch_result
        );
    }

    // 記事にチャプターを追加
    private function add_chapter_to_post($post_id, $chapter_index, $chapter_file, $outline_data) {
        $this->debug_log('Adding chapter to post:', array(
            'post_id' => $post_id,
            'chapter_index' => $chapter_index,
            'chapter_file' => $chapter_file
        ));

        // 章ファイル読み込み
        if (!file_exists($chapter_file['path'])) {
            throw new Exception('Chapter file not found: ' . $chapter_file['path']);
        }

        $chapter_content = file_get_contents($chapter_file['path']);
        
        // 既存記事取得
        $post = get_post($post_id);
        if (!$post) {
            throw new Exception('Post not found: ' . $post_id);
        }

        $existing_blocks = parse_blocks($post->post_content);
        
        // 新しいブロック作成
        $new_blocks = array();
        
        // H2見出しブロック
        $new_blocks[] = array(
            'blockName' => 'core/heading',
            'attrs' => array('level' => 2),
            'innerHTML' => '<h2 class="wp-block-heading">' . esc_html($chapter_file['title']) . '</h2>',
            'innerContent' => array('<h2 class="wp-block-heading">' . esc_html($chapter_file['title']) . '</h2>')
        );

        // サムネイル画像ブロック
        $thumbnail_block = $this->create_thumbnail_block($chapter_index + 1, $chapter_file, $outline_data);
        if ($thumbnail_block) {
            $new_blocks[] = $thumbnail_block;
        }

        // 章本文ブロック（paragraph-example.mdルールで変換）
        $content_blocks = $this->convert_content_to_blocks($chapter_content);
        $new_blocks = array_merge($new_blocks, $content_blocks);

        // ブロック結合
        $updated_blocks = array_merge($existing_blocks, $new_blocks);
        $updated_content = serialize_blocks($updated_blocks);

        // 投稿更新
        $update_result = wp_update_post(array(
            'ID' => $post_id,
            'post_content' => $updated_content
        ));

        if (is_wp_error($update_result)) {
            throw new Exception('Failed to update post: ' . $update_result->get_error_message());
        }

        $this->debug_log('Chapter added successfully:', array(
            'post_id' => $post_id,
            'blocks_added' => count($new_blocks)
        ));

        return array(
            'post_id' => $post_id,
            'blocks_added' => count($new_blocks)
        );
    }

    // まとめ文を追加
    private function add_summary_to_post($post_id, $outline_data) {
        $this->debug_log('Adding summary to post:', $post_id);

        // まとめ文ファイル検索
        $summary_file = $this->find_summary_file($outline_data['file_path']);
        $summary_content = '';
        
        if ($summary_file && file_exists($summary_file)) {
            $summary_content = file_get_contents($summary_file);
            $this->debug_log('Summary file found and loaded:', $summary_file);
        } else {
            $this->debug_log('Summary file not found, using placeholder');
            $summary_content = '<!-- wp:paragraph --><p>まとめ文を準備中...</p><!-- /wp:paragraph -->';
        }

        // 既存記事取得
        $post = get_post($post_id);
        if (!$post) {
            throw new Exception('Post not found: ' . $post_id);
        }

        $existing_blocks = parse_blocks($post->post_content);
        
        // まとめ文ブロック変換
        $summary_blocks = $this->convert_content_to_blocks($summary_content);
        
        // ブロック結合
        $updated_blocks = array_merge($existing_blocks, $summary_blocks);
        $updated_content = serialize_blocks($updated_blocks);

        // 投稿更新
        $update_result = wp_update_post(array(
            'ID' => $post_id,
            'post_content' => $updated_content
        ));

        if (is_wp_error($update_result)) {
            throw new Exception('Failed to update post: ' . $update_result->get_error_message());
        }

        $this->debug_log('Summary added successfully:', array(
            'post_id' => $post_id,
            'summary_blocks_added' => count($summary_blocks)
        ));

        return array(
            'post_id' => $post_id,
            'summary_blocks_added' => count($summary_blocks)
        );
    }

    // ===== ヘルパーメソッド =====

    // 日本語タイトル → 英語スラッグ生成
    private function generate_slug($title) {
        // TODO: Gemini APIで英語翻訳してからスラッグ化
        // 仮実装：日本語をローマ字に変換
        $slug = sanitize_title($title);
        if (empty($slug)) {
            $slug = 'blog-article-' . time();
        }
        return $slug;
    }

    // リード文ファイル検索
    private function find_lead_file($outline_path) {
        $base_path = str_replace('_outline_', '_lead_', $outline_path);
        return str_replace('.md', '.md', $base_path);
    }

    // まとめ文ファイル検索
    private function find_summary_file($outline_path) {
        $base_path = str_replace('_outline_', '_summary_', $outline_path);
        return str_replace('.md', '.md', $base_path);
    }

    // アイキャッチ画像設定
    private function set_eyecatch_image($post_id, $outline_data) {
        $this->debug_log('Setting eyecatch image for post:', $post_id);
        
        // アイキャッチ画像ファイルを検索
        $eyecatch_pattern = str_replace('_outline_', '_eyecatch_', $outline_data['file_path']);
        $eyecatch_pattern = str_replace('.md', '*.png', $eyecatch_pattern);
        
        $eyecatch_files = glob($eyecatch_pattern);
        
        if (empty($eyecatch_files)) {
            $this->debug_log('No eyecatch image found for pattern:', $eyecatch_pattern);
            return false;
        }
        
        $eyecatch_file = $eyecatch_files[0];
        $this->debug_log('Found eyecatch image:', $eyecatch_file);
        
        // 画像をWordPressメディアライブラリにアップロード
        $attachment_id = $this->upload_image_to_media_library($eyecatch_file);
        
        if ($attachment_id) {
            // アイキャッチ画像として設定
            $result = set_post_thumbnail($post_id, $attachment_id);
            $this->debug_log('Set post thumbnail result:', array(
                'post_id' => $post_id,
                'attachment_id' => $attachment_id,
                'success' => $result
            ));
            return $result;
        }
        
        return false;
    }

    // 画像をWordPressメディアライブラリにアップロード
    private function upload_image_to_media_library($file_path) {
        if (!file_exists($file_path)) {
            $this->debug_log('Image file not found:', $file_path);
            return false;
        }

        // WordPressの画像アップロード関数を使用
        require_once(ABSPATH . 'wp-admin/includes/image.php');
        require_once(ABSPATH . 'wp-admin/includes/file.php');
        require_once(ABSPATH . 'wp-admin/includes/media.php');

        $filename = basename($file_path);
        $upload_dir = wp_upload_dir();
        
        // ファイルをアップロードディレクトリにコピー
        $upload_path = $upload_dir['path'] . '/' . $filename;
        
        if (!copy($file_path, $upload_path)) {
            $this->debug_log('Failed to copy file to upload directory:', array(
                'source' => $file_path,
                'destination' => $upload_path
            ));
            return false;
        }

        // WordPress添付ファイルとして登録
        $attachment = array(
            'guid' => $upload_dir['url'] . '/' . $filename,
            'post_mime_type' => 'image/png',
            'post_title' => sanitize_file_name($filename),
            'post_content' => '',
            'post_status' => 'inherit'
        );

        $attachment_id = wp_insert_attachment($attachment, $upload_path);
        
        if (is_wp_error($attachment_id)) {
            $this->debug_log('Failed to insert attachment:', $attachment_id->get_error_message());
            return false;
        }

        // 添付ファイルのメタデータ生成
        $attach_data = wp_generate_attachment_metadata($attachment_id, $upload_path);
        wp_update_attachment_metadata($attachment_id, $attach_data);

        $this->debug_log('Successfully uploaded image to media library:', array(
            'attachment_id' => $attachment_id,
            'file_path' => $upload_path,
            'url' => $upload_dir['url'] . '/' . $filename
        ));

        return $attachment_id;
    }

    // サムネイル画像ブロック作成
    private function create_thumbnail_block($chapter_num, $chapter_file, $outline_data) {
        // TODO: サムネイル画像アップロード処理
        $this->debug_log('Creating thumbnail block for chapter:', $chapter_num);
        return null; // 仮実装
    }

    // コンテンツをブロックに変換（paragraph-example.mdルール）
    private function convert_content_to_blocks($content) {
        $this->debug_log('Converting content to blocks...');
        
        // H2見出しを除去（章見出しは別途追加するため）
        $content = preg_replace('/^## .+$/m', '', $content);
        
        // 段落ごとに分割
        $paragraphs = explode("\n\n", trim($content));
        $blocks = array();
        
        foreach ($paragraphs as $paragraph) {
            $paragraph = trim($paragraph);
            if (empty($paragraph)) {
                continue; // 空行はスキップ
            }
            
            // 表形式チェック
            if ($this->is_table_content($paragraph)) {
                $table_block = $this->create_table_block($paragraph);
                if ($table_block) {
                    $blocks[] = $table_block;
                }
                continue;
            }
            
            // 番号付きリストチェック
            if ($this->is_numbered_list($paragraph)) {
                $list_blocks = $this->create_numbered_list_blocks($paragraph);
                $blocks = array_merge($blocks, $list_blocks);
                continue;
            }
            
            // H3, H4見出しチェック
            if (preg_match('/^(#{3,4})\s+(.+)/', $paragraph, $matches)) {
                $level = strlen($matches[1]);
                $heading_text = trim($matches[2]);
                $blocks[] = $this->create_heading_block($level, $heading_text);
                continue;
            }
            
            // 通常の段落として処理
            $converted_paragraph = $this->apply_text_formatting($paragraph);
            $blocks[] = $this->create_paragraph_block($converted_paragraph);
        }
        
        $this->debug_log('Converted to blocks:', count($blocks));
        return $blocks;
    }

    // テキスト装飾を適用（paragraph-example.mdルール）
    private function apply_text_formatting($text) {
        $this->debug_log('Applying text formatting to:', substr($text, 0, 100) . '...');
        
        // 1. **文字列** → <strong>文字列</strong>
        $text = preg_replace('/\*\*([^*]+)\*\*/', '<strong>$1</strong>', $text);
        
        // 2. マーカー線用のプレースホルダー検出（重要度最高）
        // ==重要なキーワード== → <mark>重要なキーワード</mark>
        $text = preg_replace('/==([^=]+)==/', '<mark>$1</mark>', $text);
        
        // 3. 下線用のプレースホルダー検出
        // __下線テキスト__ → <u>下線テキスト</u>
        $text = preg_replace('/(?<!\*)\*([^*]+)\*(?!\*)/', '<u>$1</u>', $text);
        
        // 4. コードブロック処理
        // `code` → <code>code</code>
        $text = preg_replace('/`([^`]+)`/', '<code>$1</code>', $text);
        
        // 5. 改行処理（段落内）
        $text = str_replace("\n", '<br>', $text);
        
        $this->debug_log('Text formatting applied');
        return $text;
    }

    // 段落ブロック作成
    private function create_paragraph_block($content) {
        return array(
            'blockName' => 'core/paragraph',
            'attrs' => array(),
            'innerHTML' => '<p>' . $content . '</p>',
            'innerContent' => array('<p>' . $content . '</p>')
        );
    }

    // 見出しブロック作成
    private function create_heading_block($level, $text) {
        $tag = 'h' . $level;
        return array(
            'blockName' => 'core/heading',
            'attrs' => array('level' => $level),
            'innerHTML' => '<' . $tag . ' class="wp-block-heading">' . esc_html($text) . '</' . $tag . '>',
            'innerContent' => array('<' . $tag . ' class="wp-block-heading">' . esc_html($text) . '</' . $tag . '>')
        );
    }

    // 表形式チェック
    private function is_table_content($paragraph) {
        // | で区切られた行が複数ある場合は表とみなす
        $lines = explode("\n", $paragraph);
        $pipe_lines = 0;
        
        foreach ($lines as $line) {
            if (strpos(trim($line), '|') !== false) {
                $pipe_lines++;
            }
        }
        
        return $pipe_lines >= 2; // 2行以上のパイプ区切りがあれば表
    }

    // 表ブロック作成
    private function create_table_block($paragraph) {
        $lines = explode("\n", $paragraph);
        $table_rows = array();
        $has_header = false;
        
        foreach ($lines as $line) {
            $line = trim($line);
            if (empty($line) || strpos($line, '|') === false) {
                continue;
            }
            
            // 区切り線チェック（|---|---|）
            if (preg_match('/^\|\s*[-:]+\s*\|/', $line)) {
                $has_header = true;
                continue;
            }
            
            // セル分割
            $cells = explode('|', $line);
            $cells = array_map('trim', $cells);
            $cells = array_filter($cells, function($cell) {
                return $cell !== '';
            });
            
            if (!empty($cells)) {
                $table_rows[] = array_values($cells);
            }
        }
        
        if (empty($table_rows)) {
            return null;
        }
        
        // HTML生成
        $thead = '';
        $tbody = '';
        
        if ($has_header && !empty($table_rows)) {
            $header_row = array_shift($table_rows);
            $thead = '<thead><tr>';
            foreach ($header_row as $cell) {
                $thead .= '<th>' . esc_html($cell) . '</th>';
            }
            $thead .= '</tr></thead>';
        }
        
        if (!empty($table_rows)) {
            $tbody = '<tbody>';
            foreach ($table_rows as $row) {
                $tbody .= '<tr>';
                foreach ($row as $cell) {
                    $tbody .= '<td>' . esc_html($cell) . '</td>';
                }
                $tbody .= '</tr>';
            }
            $tbody .= '</tbody>';
        }
        
        $table_html = '<figure class="wp-block-table"><table>' . $thead . $tbody . '</table></figure>';
        
        return array(
            'blockName' => 'core/table',
            'attrs' => array(),
            'innerHTML' => $table_html,
            'innerContent' => array($table_html)
        );
    }

    // 番号付きリストチェック
    private function is_numbered_list($paragraph) {
        $lines = explode("\n", $paragraph);
        $numbered_lines = 0;
        
        foreach ($lines as $line) {
            if (preg_match('/^\d+\.\s+/', trim($line))) {
                $numbered_lines++;
            }
        }
        
        return $numbered_lines >= 2; // 2行以上の番号付きリストがあれば番号付きリスト
    }

    // 番号付きリストブロック作成
    private function create_numbered_list_blocks($paragraph) {
        $lines = explode("\n", $paragraph);
        $list_items = array();
        
        foreach ($lines as $line) {
            $line = trim($line);
            if (preg_match('/^\d+\.\s+(.+)/', $line, $matches)) {
                $list_items[] = trim($matches[1]);
            }
        }
        
        if (empty($list_items)) {
            return array();
        }
        
        $list_html = '<ol>';
        foreach ($list_items as $item) {
            $formatted_item = $this->apply_text_formatting($item);
            $list_html .= '<li>' . $formatted_item . '</li>';
        }
        $list_html .= '</ol>';
        
        return array(
            array(
                'blockName' => 'core/list',
                'attrs' => array('ordered' => true),
                'innerHTML' => $list_html,
                'innerContent' => array($list_html)
            )
        );
    }
    
    // ===== 記事更新機能のメソッド群 =====
    
    // REST API: 記事更新エンドポイント
    public function rest_update_post(WP_REST_Request $request) {
        try {
            $post_id = intval($request->get_param('id'));
            
            // 記事存在チェック
            $post = get_post($post_id);
            if (!$post) {
                return new WP_Error('post_not_found', '指定された記事が見つかりません', array('status' => 404));
            }
            
            $this->debug_log('Updating post via REST API:', array(
                'post_id' => $post_id,
                'current_title' => $post->post_title,
                'current_status' => $post->post_status
            ));
            
            // 更新データ取得
            $title = $request->get_param('title');
            $content = $request->get_param('content');
            $excerpt = $request->get_param('excerpt');
            $status = $request->get_param('status');
            $meta_description = $request->get_param('meta_description');
            $featured_image_id = $request->get_param('featured_image_id');
            $update_strategy = $request->get_param('update_strategy') ?: 'full';
            
            // バックアップ作成（オプション）
            $backup_id = null;
            if ($request->get_param('backup') === true) {
                $backup_result = $this->create_post_backup($post_id, $post);
                if (!is_wp_error($backup_result)) {
                    $backup_id = $backup_result['backup_id'];
                    $this->debug_log('Backup created:', $backup_id);
                }
            }
            
            // 更新データ構築
            $update_data = array('ID' => $post_id);
            
            if ($title !== null) {
                $update_data['post_title'] = sanitize_text_field($title);
            }
            
            if ($content !== null) {
                $update_data['post_content'] = wp_kses_post($content);
            }
            
            if ($excerpt !== null) {
                $update_data['post_excerpt'] = sanitize_text_field($excerpt);
            }
            
            if ($status !== null) {
                $update_data['post_status'] = sanitize_text_field($status);
            }
            
            // 記事更新実行
            $result = wp_update_post($update_data);
            
            if (is_wp_error($result)) {
                throw new Exception('記事の更新に失敗しました: ' . $result->get_error_message());
            }
            
            // メタデータ更新
            if ($meta_description !== null) {
                update_post_meta($post_id, '_meta_description', sanitize_text_field($meta_description));
            }
            
            // アイキャッチ画像更新
            if ($featured_image_id !== null && is_numeric($featured_image_id)) {
                if ($featured_image_id > 0) {
                    set_post_thumbnail($post_id, intval($featured_image_id));
                } else {
                    delete_post_thumbnail($post_id);
                }
            }
            
            // 更新後の記事データ取得
            $updated_post = get_post($post_id);
            
            $this->debug_log('Post updated successfully:', array(
                'post_id' => $post_id,
                'backup_id' => $backup_id,
                'update_strategy' => $update_strategy
            ));
            
            return rest_ensure_response(array(
                'success' => true,
                'post_id' => $post_id,
                'backup_id' => $backup_id,
                'modified_time' => $updated_post->post_modified,
                'edit_link' => admin_url('post.php?action=edit&post=' . $post_id),
                'preview_url' => get_preview_post_link($post_id),
                'update_strategy' => $update_strategy
            ));
            
        } catch (Exception $e) {
            $this->debug_log('Error in rest_update_post:', $e->getMessage());
            return new WP_Error('update_failed', $e->getMessage(), array('status' => 500));
        }
    }
    
    // REST API: 記事取得エンドポイント
    public function rest_get_post(WP_REST_Request $request) {
        try {
            $post_id = intval($request->get_param('id'));
            
            $post = get_post($post_id);
            if (!$post) {
                return new WP_Error('post_not_found', '指定された記事が見つかりません', array('status' => 404));
            }
            
            // 記事データ構築
            $post_data = array(
                'id' => $post->ID,
                'title' => $post->post_title,
                'content' => $post->post_content,
                'excerpt' => $post->post_excerpt,
                'status' => $post->post_status,
                'modified' => $post->post_modified,
                'created' => $post->post_date,
                'author' => $post->post_author,
                'slug' => $post->post_name
            );
            
            // メタデータ取得
            $meta_description = get_post_meta($post_id, '_meta_description', true);
            if ($meta_description) {
                $post_data['meta_description'] = $meta_description;
            }
            
            // アイキャッチ画像取得
            $featured_image_id = get_post_thumbnail_id($post_id);
            if ($featured_image_id) {
                $post_data['featured_image_id'] = $featured_image_id;
                $post_data['featured_image_url'] = wp_get_attachment_url($featured_image_id);
            }
            
            $this->debug_log('Post retrieved successfully:', array(
                'post_id' => $post_id,
                'title' => $post->post_title
            ));
            
            return rest_ensure_response($post_data);
            
        } catch (Exception $e) {
            $this->debug_log('Error in rest_get_post:', $e->getMessage());
            return new WP_Error('get_failed', $e->getMessage(), array('status' => 500));
        }
    }
    
    // REST API: バックアップ作成エンドポイント
    public function rest_backup_post(WP_REST_Request $request) {
        try {
            $post_id = intval($request->get_param('id'));
            
            $post = get_post($post_id);
            if (!$post) {
                return new WP_Error('post_not_found', '指定された記事が見つかりません', array('status' => 404));
            }
            
            $backup_data = $request->get_json_params();
            $result = $this->create_post_backup($post_id, $post, $backup_data);
            
            if (is_wp_error($result)) {
                throw new Exception($result->get_error_message());
            }
            
            return rest_ensure_response($result);
            
        } catch (Exception $e) {
            $this->debug_log('Error in rest_backup_post:', $e->getMessage());
            return new WP_Error('backup_failed', $e->getMessage(), array('status' => 500));
        }
    }
    
    // REST API: バックアップ復元エンドポイント
    public function rest_restore_post(WP_REST_Request $request) {
        try {
            $post_id = intval($request->get_param('id'));
            $backup_id = $request->get_param('backup_id');
            
            if (!$backup_id) {
                return new WP_Error('invalid_backup', 'バックアップIDが指定されていません', array('status' => 400));
            }
            
            $result = $this->restore_post_from_backup($post_id, $backup_id);
            
            if (is_wp_error($result)) {
                throw new Exception($result->get_error_message());
            }
            
            return rest_ensure_response($result);
            
        } catch (Exception $e) {
            $this->debug_log('Error in rest_restore_post:', $e->getMessage());
            return new WP_Error('restore_failed', $e->getMessage(), array('status' => 500));
        }
    }
    
    // REST API: 記事検索エンドポイント
    public function rest_search_posts(WP_REST_Request $request) {
        try {
            $title = $request->get_param('title');
            $fuzzy = $request->get_param('fuzzy') !== 'false';
            
            if (!$title) {
                return rest_ensure_response(array());
            }
            
            $search_args = array(
                'post_type' => 'post',
                'post_status' => array('publish', 'draft'),
                'posts_per_page' => 10,
                's' => $title
            );
            
            if ($fuzzy) {
                // ファジー検索の場合はより緩い条件で検索
                $search_args['meta_query'] = array(
                    'relation' => 'OR',
                    array(
                        'key' => '_meta_description',
                        'value' => $title,
                        'compare' => 'LIKE'
                    )
                );
            }
            
            $posts = get_posts($search_args);
            $results = array();
            
            foreach ($posts as $post) {
                $results[] = array(
                    'id' => $post->ID,
                    'title' => $post->post_title,
                    'status' => $post->post_status,
                    'modified' => $post->post_modified,
                    'excerpt' => wp_trim_words($post->post_content, 20)
                );
            }
            
            return rest_ensure_response($results);
            
        } catch (Exception $e) {
            $this->debug_log('Error in rest_search_posts:', $e->getMessage());
            return rest_ensure_response(array());
        }
    }
    
    // REST API: 記事分析データ取得エンドポイント
    public function rest_get_analytics(WP_REST_Request $request) {
        try {
            $post_id = intval($request->get_param('id'));
            
            $post = get_post($post_id);
            if (!$post) {
                return new WP_Error('post_not_found', '指定された記事が見つかりません', array('status' => 404));
            }
            
            // 基本分析データ
            $analytics = array(
                'post_id' => $post_id,
                'word_count' => str_word_count(strip_tags($post->post_content)),
                'character_count' => mb_strlen(strip_tags($post->post_content)),
                'paragraph_count' => substr_count($post->post_content, '</p>'),
                'last_modified' => $post->post_modified,
                'status' => $post->post_status
            );
            
            // 見出し数カウント
            $analytics['heading_count'] = array(
                'h2' => substr_count($post->post_content, '<h2'),
                'h3' => substr_count($post->post_content, '<h3'),
                'h4' => substr_count($post->post_content, '<h4')
            );
            
            // アイキャッチ画像情報
            $featured_image_id = get_post_thumbnail_id($post_id);
            $analytics['has_featured_image'] = !empty($featured_image_id);
            
            return rest_ensure_response($analytics);
            
        } catch (Exception $e) {
            $this->debug_log('Error in rest_get_analytics:', $e->getMessage());
            return rest_ensure_response(array());
        }
    }
    
    // バックアップ作成
    private function create_post_backup($post_id, $post, $additional_data = array()) {
        try {
            $backup_id = 'backup_' . $post_id . '_' . time() . '_' . wp_generate_password(8, false);
            
            $backup_data = array(
                'post_id' => $post_id,
                'post_title' => $post->post_title,
                'post_content' => $post->post_content,
                'post_excerpt' => $post->post_excerpt,
                'post_status' => $post->post_status,
                'post_modified' => $post->post_modified,
                'meta_description' => get_post_meta($post_id, '_meta_description', true),
                'featured_image_id' => get_post_thumbnail_id($post_id),
                'backup_created' => current_time('mysql'),
                'additional_data' => $additional_data
            );
            
            // バックアップをオプションとして保存（一時的な実装）
            update_option('blog_generator_backup_' . $backup_id, $backup_data);
            
            $this->debug_log('Backup created successfully:', array(
                'backup_id' => $backup_id,
                'post_id' => $post_id
            ));
            
            return array(
                'backup_id' => $backup_id,
                'created_at' => current_time('mysql'),
                'post_title' => $post->post_title
            );
            
        } catch (Exception $e) {
            $this->debug_log('Error creating backup:', $e->getMessage());
            return new WP_Error('backup_failed', 'バックアップの作成に失敗しました: ' . $e->getMessage());
        }
    }
    
    // バックアップから復元
    private function restore_post_from_backup($post_id, $backup_id) {
        try {
            $backup_data = get_option('blog_generator_backup_' . $backup_id);
            
            if (!$backup_data) {
                return new WP_Error('backup_not_found', 'バックアップが見つかりません');
            }
            
            if ($backup_data['post_id'] != $post_id) {
                return new WP_Error('backup_mismatch', 'バックアップの記事IDが一致しません');
            }
            
            // 記事復元
            $restore_data = array(
                'ID' => $post_id,
                'post_title' => $backup_data['post_title'],
                'post_content' => $backup_data['post_content'],
                'post_excerpt' => $backup_data['post_excerpt'],
                'post_status' => $backup_data['post_status']
            );
            
            $result = wp_update_post($restore_data);
            
            if (is_wp_error($result)) {
                throw new Exception('記事の復元に失敗しました: ' . $result->get_error_message());
            }
            
            // メタデータ復元
            if ($backup_data['meta_description']) {
                update_post_meta($post_id, '_meta_description', $backup_data['meta_description']);
            }
            
            // アイキャッチ画像復元
            if ($backup_data['featured_image_id']) {
                set_post_thumbnail($post_id, $backup_data['featured_image_id']);
            }
            
            $this->debug_log('Post restored successfully:', array(
                'post_id' => $post_id,
                'backup_id' => $backup_id
            ));
            
            return array(
                'post_id' => $post_id,
                'backup_id' => $backup_id,
                'restored_time' => current_time('mysql'),
                'restored_title' => $backup_data['post_title']
            );
            
        } catch (Exception $e) {
            $this->debug_log('Error restoring backup:', $e->getMessage());
            return new WP_Error('restore_failed', 'バックアップの復元に失敗しました: ' . $e->getMessage());
        }
    }
}

// プラグインのインスタンスを初期化
function blog_generator_plugin_init() {
    Blog_Generator_Plugin::get_instance();
}
add_action('plugins_loaded', 'blog_generator_plugin_init');