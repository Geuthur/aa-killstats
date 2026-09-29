
// React
import { Outlet } from "react-router";

// Third Party
import { Col } from "react-bootstrap";

import { ErrorBoundary } from "@/Components/Loader";
import AuthLeftMenuAsync from "@/Menu/AuthLeftMenuAsync";
import AuthRightMenuAsync from "@/Menu/AuthRightMenuAsync";

const AuthBase = () => {
  return (
    <>
      <AuthLeftMenuAsync />
      <AuthRightMenuAsync />
      <Col>
        <div className="mt-4 tw-priority">
          <ErrorBoundary>
            <Outlet /> {/* Render the Children here */}
          </ErrorBoundary>
        </div>
      </Col>
    </>
  );
};

export default AuthBase;
