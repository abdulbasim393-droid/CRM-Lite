import { useEffect, useState } from 'react';
import { Card, CardBody } from '../components/ui/Card';
import { DataTable, type Column } from '../components/ui/DataTable';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { customersApi } from '../api/customers';
import type { Customer } from '../types';

export function CustomersPage() {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    customersApi.list()
      .then((res) => setCustomers(res.data))
      .finally(() => setLoading(false));
  }, []);

  const columns: Column<Customer>[] = [
    { key: 'first_name', header: 'Name', sortable: true, render: (r) => `${r.first_name} ${r.last_name}` },
    { key: 'company', header: 'Company', sortable: true },
    { key: 'phone', header: 'Phone' },
    { key: 'email', header: 'Email' },
    { key: 'converted_at', header: 'Converted', sortable: true, render: (r) => new Date(r.converted_at).toLocaleDateString() },
    { key: 'created_by_name', header: 'Created By' },
  ];

  return (
    <Card>
      <CardBody>
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Customers</h2>
        <DataTable columns={columns} data={customers} keyExtractor={(r) => r.id} loading={loading} emptyMessage="No customers yet. Convert WON leads to create customers." />
      </CardBody>
    </Card>
  );
}
