import { useState, useRef, useEffect } from 'react';
import { FileText, Download, Copy, Trash2 } from 'lucide-react';
import './VerticalTextEditor.css';

export function VerticalTextEditor() {
  const [text, setText] = useState<string>('');
  const [charCount, setCharCount] = useState<number>(0);
  const [lineCount, setLineCount] = useState<number>(1);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    const lines = text.split('\n').length;
    const chars = text.length;
    setLineCount(lines);
    setCharCount(chars);
  }, [text]);

  const handleTextChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setText(e.target.value);
  };

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(text);
      alert('テキストをコピーしました');
    } catch (err) {
      console.error('コピーに失敗しました:', err);
    }
  };

  const handleDownload = () => {
    const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `vertical-text-${new Date().toISOString().split('T')[0]}.txt`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const handleClear = () => {
    if (text.length === 0 || window.confirm('テキストをすべて削除しますか?')) {
      setText('');
      textareaRef.current?.focus();
    }
  };

  return (
    <div className="vertical-text-editor">
      <div className="editor-header">
        <div className="header-left">
          <FileText size={24} />
          <h2>縦書きテキストエディタ</h2>
        </div>
        <div className="editor-stats">
          <span className="stat">
            <strong>文字数:</strong> {charCount}
          </span>
          <span className="stat">
            <strong>行数:</strong> {lineCount}
          </span>
        </div>
      </div>

      <div className="editor-toolbar">
        <button
          className="toolbar-button"
          onClick={handleCopy}
          disabled={text.length === 0}
          title="テキストをコピー"
        >
          <Copy size={18} />
          <span>コピー</span>
        </button>
        <button
          className="toolbar-button"
          onClick={handleDownload}
          disabled={text.length === 0}
          title="テキストをダウンロード"
        >
          <Download size={18} />
          <span>ダウンロード</span>
        </button>
        <button
          className="toolbar-button danger"
          onClick={handleClear}
          disabled={text.length === 0}
          title="テキストをクリア"
        >
          <Trash2 size={18} />
          <span>クリア</span>
        </button>
      </div>

      <div className="editor-container">
        <textarea
          ref={textareaRef}
          className="vertical-textarea"
          value={text}
          onChange={handleTextChange}
          placeholder="ここに縦書きで文章を入力してください&#10;改行すると右から左へ列が増えます&#10;&#10;例：&#10;吾輩は猫である。&#10;名前はまだ無い。"
          spellCheck="false"
        />
      </div>

      <div className="editor-footer">
        <p className="editor-description">
          このエディタは日本語の縦書き表示に対応しています。
          テキストは右から左へ、上から下へと流れます。
        </p>
      </div>
    </div>
  );
}
