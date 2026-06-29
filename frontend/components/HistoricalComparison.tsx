"use client";

interface QuantityChange {
  symbol: string;
  previous_quantity: number;
  current_quantity: number;
  change: number;
}

interface ComparisonData {
  added_holdings: string[];
  removed_holdings: string[];
  quantity_changes: QuantityChange[];
}

interface HistoricalComparisonProps {
  data: ComparisonData | null;
}

export default function HistoricalComparison({
  data,
}: HistoricalComparisonProps) {
  if (!data) {
    return (
      <div className="mt-6 bg-white rounded-xl shadow-md p-6">
        <p className="text-gray-500">
          Loading historical comparison...
        </p>
      </div>
    );
  }

  const noChanges =
    data.added_holdings.length === 0 &&
    data.removed_holdings.length === 0 &&
    data.quantity_changes.length === 0;

  return (
    <div className="mt-6 bg-white rounded-xl shadow-md p-6">
      <h2 className="text-2xl font-semibold mb-6 text-black">
        Historical Portfolio Comparison
      </h2>

      {noChanges ? (
        <p className="text-gray-600">No portfolio changes detected.</p>
      ) : (
        <div className="space-y-6">

          <div>
            <h3 className="font-semibold text-green-700 mb-2">
              Added Holdings
            </h3>

            {data.added_holdings.length > 0 ? (
              <ul className="list-disc ml-6 text-black">
                {data.added_holdings.map((holding) => (
                  <li key={holding}>{holding}</li>
                ))}
              </ul>
            ) : (
              <p className="text-gray-500">None</p>
            )}
          </div>

          <div>
            <h3 className="font-semibold text-red-700 mb-2">
              Removed Holdings
            </h3>

            {data.removed_holdings.length > 0 ? (
              <ul className="list-disc ml-6 text-black">
                {data.removed_holdings.map((holding) => (
                  <li key={holding}>{holding}</li>
                ))}
              </ul>
            ) : (
              <p className="text-gray-500">None</p>
            )}
          </div>

          <div>
            <h3 className="font-semibold text-blue-700 mb-2">
              Quantity Changes
            </h3>

            {data.quantity_changes.length > 0 ? (
              <table className="w-full border border-gray-300">
                <thead className="bg-gray-100">
                  <tr>
                    <th className="border p-2 text-left text-black">Symbol</th>
                    <th className="border p-2 text-left text-black">Previous</th>
                    <th className="border p-2 text-left text-black">Current</th>
                    <th className="border p-2 text-left text-black">Change</th>
                  </tr>
                </thead>

                <tbody>
                  {data.quantity_changes.map((item) => (
                    <tr key={item.symbol}>
                      <td className="border p-2 text-black">{item.symbol}</td>
                      <td className="border p-2 text-black">
                        {item.previous_quantity}
                      </td>
                      <td className="border p-2 text-black">
                        {item.current_quantity}
                      </td>
                      <td className="border p-2 text-green-600 font-semibold">
                        +{item.change}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <p className="text-gray-500">None</p>
            )}
          </div>

        </div>
      )}
    </div>
  );
}