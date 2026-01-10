/**
 * main.js - LocalStorage操作関数
 * 受け取った短歌をブラウザに保存
 */

const STORAGE_KEY = 'tanka_history';

/**
 * 短歌を履歴に保存
 * @param {string} content - 短歌の内容
 */
function saveTankaToHistory(content) {
    const history = getTankaHistory();

    const item = {
        content: content,
        timestamp: new Date().toISOString()
    };

    history.push(item);

    // 最大100件まで保存
    if (history.length > 100) {
        history.shift();
    }

    localStorage.setItem(STORAGE_KEY, JSON.stringify(history));
}

/**
 * 履歴を取得
 * @returns {Array} 履歴の配列
 */
function getTankaHistory() {
    const data = localStorage.getItem(STORAGE_KEY);
    if (!data) {
        return [];
    }

    try {
        return JSON.parse(data);
    } catch (e) {
        console.error('履歴の読み込みに失敗:', e);
        return [];
    }
}

/**
 * 履歴をクリア
 */
function clearHistory() {
    localStorage.removeItem(STORAGE_KEY);
}

/**
 * 履歴の件数を取得
 * @returns {number} 履歴の件数
 */
function getHistoryCount() {
    return getTankaHistory().length;
}
