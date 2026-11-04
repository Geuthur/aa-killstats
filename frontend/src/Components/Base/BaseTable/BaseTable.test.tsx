// React
import { MemoryRouter } from "react-router-dom";

// Third Party
import "@testing-library/jest-dom/vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import BaseTable from "@/Components/Base/BaseTable/BaseTable";
import { createBaseColumnHelper } from "@/Components/Base/BaseTable/tableFeatures";

vi.mock("react-i18next", async (importOriginal) => ({
  ...(await importOriginal<typeof import("react-i18next")>()),
  useTranslation: () => ({
    t: (key: string, options?: Record<string, unknown>) =>
      options
        ? Object.entries(options).reduce(
          (text, [name, value]) => text.replace(`{{${name}}}`, String(value)),
          key,
        )
        : key,
  }),
}));

interface TestRow {
  id: number;
  name: string;
  role: string;
}

const columnHelper = createBaseColumnHelper<TestRow>();

const testColumns = [
  columnHelper.accessor("name", {
    header: "Name",
    enableColumnFilter: true,
  }),
  columnHelper.accessor("role", {
    header: "Role",
    enableColumnFilter: true,
  }),
];

const testData: TestRow[] = [
  { id: 1, name: "Alice", role: "Pilot" },
  { id: 2, name: "Bob", role: "Miner" },
  { id: 3, name: "Charlie", role: "Industrialist" },
];

const renderTable = (props?: Partial<React.ComponentProps<typeof BaseTable<TestRow>>>) => {
  return render(
    <MemoryRouter>
      <BaseTable
        columns={testColumns}
        data={testData}
        {...props}
      />
    </MemoryRouter>,
  );
};

describe("BaseTable", () => {
  it("test_render_should_display_aa_table_with_data", () => {
    // Test Data
    const data = testData;

    // Test Action
    const { container } = renderTable({ data });

    // Expected Result
    expect(container.querySelector(".aa-table-shell")).toBeInTheDocument();
    expect(container.querySelector(".aa-table")).toBeInTheDocument();
    expect(screen.getByText("Alice")).toBeInTheDocument();
    expect(screen.getByText("Bob")).toBeInTheDocument();
    expect(screen.getByText("Charlie")).toBeInTheDocument();
  });

  it("test_render_should_display_empty_text_when_no_data", () => {
    // Test Data
    const emptyText = "No pilot records available";

    // Test Action
    renderTable({ data: [], emptyText });

    // Expected Result
    expect(screen.getByText(emptyText)).toBeInTheDocument();
  });

  it("test_sort_should_toggle_sorting_direction_on_header_click", async () => {
    // Test Data
    const user = userEvent.setup();
    renderTable();

    // Test Action: Click sort header
    const nameHeader = screen.getByText("Name");
    await user.click(nameHeader);

    // Expected Result: Alice is first in ascending order
    const cells = screen.getAllByRole("cell");
    expect(cells[0]).toHaveTextContent("Alice");

    // Test Action: Click sort header again for descending
    await user.click(nameHeader);

    // Expected Result: Charlie is first in descending order
    const cellsDesc = screen.getAllByRole("cell");
    expect(cellsDesc[0]).toHaveTextContent("Charlie");
  });

  it("test_filter_should_render_filter_inputs_when_enabled", () => {
    // Test Data & Test Action
    const { container } = renderTable({ enableFilters: true });

    // Expected Result
    expect(container.querySelector(".aa-table-filter-row")).toBeInTheDocument();
    expect(container.querySelectorAll(".aa-table-filter-cell").length).toBe(2);
  });

  it("test_filter_should_hide_rows_not_matching_the_text_filter", async () => {
    // Test Data
    const user = userEvent.setup();
    const { container } = renderTable({ enableFilters: true });
    const nameFilter = container.querySelectorAll(".aa-table-filter-cell input")[0] as HTMLInputElement;

    // Test Action
    await user.type(nameFilter, "bo");

    // Expected Result: only Bob's row is left (the filter dropdown lists names too, so check the cells)
    const names = Array.from(container.querySelectorAll(".aa-table-body tr td:first-child")).map(
      (cell) => cell.textContent,
    );
    expect(names).toEqual(["Bob"]);
  });

  it("test_filter_should_omit_filter_row_when_disabled", () => {
    // Test Data & Test Action
    const { container } = renderTable({ enableFilters: false });

    // Expected Result
    expect(container.querySelector(".aa-table-filter-row")).not.toBeInTheDocument();
  });

  it("test_pagination_should_navigate_pages_when_page_size_exceeded", async () => {
    // Test Data
    const user = userEvent.setup();
    const lotsOfData: TestRow[] = Array.from({ length: 25 }, (_, i) => ({
      id: i + 1,
      name: `Pilot ${i + 1}`,
      role: "Member",
    }));

    // Test Action
    renderTable({
      data: lotsOfData,
      initialState: { pagination: { pageSize: 10 } },
      pageSizeOptions: [10, 25],
    });

    // Expected Result: Page 1 shows first 10
    expect(screen.getByText("Pilot 1")).toBeInTheDocument();
    expect(screen.queryByText("Pilot 15")).not.toBeInTheDocument();

    // Test Action: Click Next Page
    const nextBtn = screen.getByTitle("Next Page");
    await user.click(nextBtn);

    // Expected Result: Page 2 shows next 10
    expect(screen.getByText("Pilot 15")).toBeInTheDocument();
    expect(screen.queryByText("Pilot 1")).not.toBeInTheDocument();
  });

  it("test_row_click_should_call_on_row_click_with_row", async () => {
    // Test Data
    const user = userEvent.setup();
    const onRowClick = vi.fn();
    renderTable({ onRowClick });

    // Test Action
    await user.click(screen.getByText("Bob"));

    // Expected Result
    expect(onRowClick).toHaveBeenCalledTimes(1);
    expect(onRowClick.mock.calls[0][0].original).toEqual(testData[1]);
  });

  it("test_row_selection_should_report_selected_rows_by_row_id", async () => {
    // Test Data
    const user = userEvent.setup();
    const onRowSelectionChange = vi.fn();
    const selectColumn = columnHelper.display({
      id: "select",
      cell: ({ row }) => (
        <input
          type="checkbox"
          aria-label={`select-${row.original.id}`}
          checked={row.getIsSelected()}
          onChange={row.getToggleSelectedHandler()}
        />
      ),
    });
    renderTable({
      columns: [selectColumn, ...testColumns] as typeof testColumns,
      getRowId: (row) => String(row.id),
      rowSelection: {},
      onRowSelectionChange,
      enableRowSelection: true,
    });

    // Test Action
    await user.click(screen.getByLabelText("select-2"));

    // Expected Result
    expect(onRowSelectionChange).toHaveBeenCalledTimes(1);
    const updater = onRowSelectionChange.mock.calls[0][0];
    expect(typeof updater === "function" ? updater({}) : updater).toEqual({ "2": true });
  });

  describe("serverPagination", () => {
    const renderServerTable = (
      serverPagination?: Partial<NonNullable<React.ComponentProps<typeof BaseTable<TestRow>>["serverPagination"]>>,
      props?: Partial<React.ComponentProps<typeof BaseTable<TestRow>>>,
    ) => {
      const pagination = {
        page: 2,
        pageSize: 2,
        total: 10,
        onPageChange: vi.fn(),
        onPageSizeChange: vi.fn(),
        ...serverPagination,
      };
      return { pagination, ...renderTable({ serverPagination: pagination, ...props }) };
    };

    it("test_server_pagination_should_show_all_given_rows_and_the_server_page_count", () => {
      // Test Data & Test Action: three rows on a page of two must not be sliced again
      renderServerTable();

      // Expected Result
      expect(screen.getByText("Alice")).toBeInTheDocument();
      expect(screen.getByText("Charlie")).toBeInTheDocument();
      expect(screen.getAllByText("Page 2 of 5").length).toBeGreaterThan(0);
    });

    it("test_server_pagination_should_report_one_based_pages_from_the_buttons", async () => {
      // Test Data
      const user = userEvent.setup();
      const { pagination } = renderServerTable();

      // Test Action & Expected Result
      await user.click(screen.getByTitle("Next Page"));
      expect(pagination.onPageChange).toHaveBeenLastCalledWith(3);
      await user.click(screen.getByTitle("Previous Page"));
      expect(pagination.onPageChange).toHaveBeenLastCalledWith(1);
      await user.click(screen.getByTitle("First Page"));
      expect(pagination.onPageChange).toHaveBeenLastCalledWith(1);
      await user.click(screen.getByTitle("Last Page"));
      expect(pagination.onPageChange).toHaveBeenLastCalledWith(5);
    });

    it("test_server_pagination_should_report_only_the_page_size_when_it_changes", async () => {
      // Test Data
      const user = userEvent.setup();
      const { pagination } = renderServerTable(undefined, { pageSizeOptions: [2, 25] });

      // Test Action
      await user.selectOptions(screen.getByRole("combobox"), "25");

      // Expected Result
      expect(pagination.onPageSizeChange).toHaveBeenCalledWith(25);
      expect(pagination.onPageChange).not.toHaveBeenCalled();
    });

    it("test_server_pagination_should_disable_buttons_at_the_boundaries", () => {
      // Test Data & Test Action
      renderServerTable({ page: 1 });

      // Expected Result
      expect(screen.getByTitle("First Page")).toBeDisabled();
      expect(screen.getByTitle("Previous Page")).toBeDisabled();
      expect(screen.getByTitle("Next Page")).toBeEnabled();
      expect(screen.getByTitle("Last Page")).toBeEnabled();
    });

    it("test_server_pagination_should_show_the_total", () => {
      // Test Data & Test Action
      renderServerTable({ total: 1234 });

      // Expected Result
      expect(screen.getByText(/Total: 1,?234/)).toBeInTheDocument();
    });

    it("test_server_pagination_should_prefer_the_given_total_text", () => {
      // Test Data & Test Action
      renderServerTable({ totalText: "10 killmails" });

      // Expected Result
      expect(screen.getByText("10 killmails")).toBeInTheDocument();
      expect(screen.queryByText(/Total:/)).not.toBeInTheDocument();
    });

    it("test_server_pagination_should_hide_tools_that_only_see_the_current_page", async () => {
      // Test Data
      const user = userEvent.setup();

      // Test Action
      const { container } = renderServerTable();
      await user.click(screen.getByText("Name"));

      // Expected Result: no show all, CSV export, filters or sorting; row order is the server's
      expect(screen.queryByRole("option", { name: "Show All" })).not.toBeInTheDocument();
      expect(screen.queryByRole("button", { name: "Export Table to CSV" })).not.toBeInTheDocument();
      expect(container.querySelector(".aa-table-filter-row")).not.toBeInTheDocument();
      expect(container.querySelector(".aa-table-sortable")).not.toBeInTheDocument();
    });
  });

  describe("isLoading", () => {
    it("test_loading_should_show_the_loader_instead_of_the_empty_text_without_rows", () => {
      // Test Data & Test Action
      const { container } = renderTable({ data: [], isLoading: true, emptyText: "Nothing here" });

      // Expected Result
      expect(screen.queryByText("Nothing here")).not.toBeInTheDocument();
      expect(container.querySelector(".aa-table-message [role='status']")).toBeInTheDocument();
      expect(container.querySelector(".aa-table-loading")).not.toBeInTheDocument();
    });

    it("test_loading_should_show_the_given_loading_text", () => {
      // Test Data & Test Action
      renderTable({ data: [], isLoading: true, loadingText: "Loading pilots..." });

      // Expected Result
      expect(screen.getByText("Loading pilots...")).toBeInTheDocument();
    });

    it("test_loading_should_dim_the_visible_rows_and_lock_the_controls", () => {
      // Test Data & Test Action
      const lotsOfData: TestRow[] = Array.from({ length: 25 }, (_, i) => ({
        id: i + 1,
        name: `Pilot ${i + 1}`,
        role: "Member",
      }));
      const { container } = renderTable({
        data: lotsOfData,
        isLoading: true,
        initialState: { pagination: { pageSize: 10 } },
      });

      // Expected Result
      expect(screen.getByText("Pilot 1")).toBeInTheDocument();
      expect(container.querySelector(".aa-table-loading")).toBeInTheDocument();
      expect(screen.getByRole("combobox")).toBeDisabled();
      expect(screen.getByTitle("Next Page")).toBeDisabled();
      expect(screen.getByTitle("Last Page")).toBeDisabled();
    });

    it("test_loading_should_not_change_the_table_by_default", () => {
      // Test Data & Test Action
      const { container } = renderTable();

      // Expected Result
      expect(container.querySelector(".aa-table-loading")).not.toBeInTheDocument();
      expect(screen.getByRole("combobox")).toBeEnabled();
      expect(screen.getByRole("option", { name: "Show All" })).toBeInTheDocument();
      expect(screen.getByRole("button", { name: "Export Table to CSV" })).toBeInTheDocument();
    });
  });
});
