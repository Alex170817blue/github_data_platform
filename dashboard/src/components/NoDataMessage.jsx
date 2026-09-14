export default function NoDataMessage({ message = 'No data available', height = 300 }) {
  return (
    <div style={{ 
      display: 'flex', 
      justifyContent: 'center', 
      alignItems: 'center', 
      height,
      color: '#810202',
      fontSize: '14px',
      background: '#fafafa',
      borderRadius: '8px',
      border: '1px dashed #ddd'
    }}>
      {message}
    </div>
  );
}